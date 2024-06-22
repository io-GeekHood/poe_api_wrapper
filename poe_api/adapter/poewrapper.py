import re, json, random, time, queue, threading, traceback, hashlib, string, random
import websocket
import random
from pathlib import Path
from urllib.parse import urlparse
from poe_api.config.config import *
import time
import logging
from python_graphql_client import GraphqlClient
import requests
from typing import Any, Dict, Iterator, List, Mapping, Optional, Literal, Tuple, Union
from poe_api.config.config_model import PoeConfig, ChatCompletionRequest, Message
from websockets_proxy import Proxy, proxy_connect
from poe_api.util.history_manager import HistoryManager
from pprint import pprint
import websocket


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PoeApi(HistoryManager):
    gql_url = "https://poe.com/api/gql_POST"
    gql_recv_url = "https://poe.com/api/receive_POST"
    home_url = "https://poe.com"
    # settings_url = f"https://poe.com/api/settings?channel={SOCKET_CHANNEL3['channel']}"

    def __init__(self, init_config:PoeConfig):
        # for key,value in init_config.model_dump(by_alias=True).items():
        #     setattr(self,key,value)

        self.config = init_config
        self.global_headers = init_config.Headers.model_dump(by_alias=True)
        self.proxies = init_config.Proxies.model_dump(by_alias=True)
        self.cookies = init_config.Cookies.model_dump(by_alias=True)
        self.ws_connecting = False
        self.ws_connected = False
        self.ws_error = False
        self.connect_count = 0
        self.setup_count = 0
        self.setup_connection()
        # self.connect_ws()
        
        self.parent_prompt = """
        تو یک دستیار هوشمند بیمه فارسی به نام آناهیتا هستی, از شما انتظار دارم در قالب مشخص شده حاوی تگ های 
        <سوال>
        متن سوال اینجا قرار میگیرد
        <پایان سوال>
        <زمینه>
        مطالب زمینه اینجا قرار میگیرند
        <پایان زمینه>
        با خواندن مطالب موجود در تگ <زمینه> قست های مرتبط با سوال من رو پیدا کن و به درخواست من در قسمت <سوال> پاسخ بده
        در تمام طول مکالمه این موارد را رعایت کن:
        سعی کن پاسخ کامل و حتما بر اساس اطلاعات داخل قسمت <زمینه> باشدو از دانش قبلی خودت استفاده ایی نکنی
        پاسخ خود را همیشه با کلمات 'طبق اطلاعات من' شروع کن
        اگر درخواست من در خصوص توضیح بیشتر در مورد قسمتی از مکالمه بود پاسخ من را از قسمت زمینه پیام قبل بده و زمینه جدید را نادیده بگیر
        """


    def setup_connection(self):
        """
        Initializes the GraphQL client with specific configurations and retrieves the WebSocket channel information.

        Inputs:
        - self: An instance of the PoeApi class.

        Outputs:
        - Initializes the self.client with a GraphqlClient instance.
        - Sets the self.ws_domain with a randomly generated domain name.
        - Sets the self.channel with the channel information retrieved from the get_channel method.
        """
        self.client = GraphqlClient(endpoint=self.config.GqlUri, headers=self.global_headers, proxies=self.proxies['format'], cookies=self.cookies)
        self.ws_domain = f"tch{random.randint(1, 1e6)}"
        self.channel = self.get_channel()
        
    def get_channel(self) -> dict:
        """
        Fetches WebSocket channel settings from a specified URL using HTTP GET request.

        Returns:
        dict: JSON response from the settings URL if the request is successful.

        Logs an error message if the request fails.
        """
        try:
            response = requests.get(self.config.SettingsUrl, proxies=self.proxies['format'], headers=self.global_headers)
            return response.json()
        except Exception as fail:
            logger.error(f"Failed to fetch wss channel settings from {self.config.SettingsUrl} | {fail}")
    def generate_ws_url(self, channel=None) -> str:
        """
        Constructs a WebSocket URL for connecting to a specific channel.

        Args:
            channel (dict, optional): Dictionary containing channel data. Defaults to None.

        Returns:
            str: The constructed WebSocket URL.
        """
        if channel is None:
            channel = self.channel

        try:
            channel = channel['tchannelData']
        except KeyError:
            logger.error(f"Expected valid channel info from setting uri, got {channel}")
            raise

        query_params = {
            'min_seq': channel["minSeq"],
            'channel': channel["channel"],
            'hash': channel["channelHash"],
            'generation': 1
        }
        query = '?' + '&'.join([f'{key}={value}' for key, value in query_params.items()])

        uri = f'ws://{self.ws_domain}.tch.{channel["baseHost"]}/up/{channel["boxName"]}/updates{query}'
        logger.info(f"Successfully created new channel: {uri}")

        return uri

    def operation_builder(
        self, operation_name: Literal["bot-pagination", "message-edge", "bot-query", "chat-pagination", "chat-list", "bots-explore", "subscription"]
    ) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
        """
        Constructs a GraphQL query, its variables, and headers required for a specific operation.

        Args:
            operation_name: A literal string specifying the name of the operation.

        Returns:
            query: The GraphQL query string.
            target_vars: The variables required for the query.
            headers: The updated headers for the request.
        """
        headers = self.global_headers
        ops_info = self.config.Operations.model_dump(by_alias=True)[operation_name]
        headers.update(ops_info)
        with open(f"./assets/poe_gql/variables.json", "r", encoding="utf-8") as var:
            allvars = json.load(var)
            target_vars = allvars[ops_info['x-apollo-operation-name']]

        with open(
            f"./assets/poe_gql/{ops_info['x-apollo-operation-name']}.graphql",
            "r",
            encoding="utf-8",
        ) as query_file:
            query = query_file.read()

        return query, target_vars, headers
    
    async def send_message(self, request: ChatCompletionRequest, token: str = ""):
        """
        Sends a chat message to the poe WebSocket server via a proxy, processes the response, and returns the text response and chat ID.

        Args:
            request (ChatCompletionRequest): An instance of ChatCompletionRequest containing the chat message and other parameters.
            token (str): A string token used to identify the chat session.

        Returns:
            tuple: A tuple containing the text response and the chat ID.
        """
        ws_headers = self.config.WSHeaders.model_dump(by_alias=True)
        proxy = Proxy.from_url(self.proxies['uri'])
        logger.info(f"Connecting via proxy URI {self.proxies['uri']}")
        
        ws_url = self.generate_ws_url()
        ws_headers["Host"] = f"{self.ws_domain}.tch.poe.com"
        
        async with proxy_connect(ws_url, extra_headers=ws_headers, proxy=proxy) as websocket:
            query, variables, gqlheaders = self.operation_builder(operation_name="message-edge")
            
            chat_history = self.get_chat_history(token)
            stored_ids = set(chat_history.get("message_ids", []))
            
            variables["query"] = request.messages[0].content[0].text
            variables["bot"] = request.model
            variables["chatId"] = chat_history.get("chat_id", "")
            variables["messagePointPrice"] = self.config.PriceMapping.get(request.model, 0)
            operation_name = self.config.Operations.model_dump(by_alias=True)["message-edge"]["x-apollo-operation-name"]
            gql_execution_info = await self.client.execute_async(
                query=query,
                variables=variables,
                operation_name=operation_name,
                headers=gqlheaders,
            )
            
            chat_id = gql_execution_info["data"]["messageEdgeCreate"]["chat"]["chatId"]
            idx = 0
            complete = False
            text_response = ""
            logger.warning(f"Invoking \n {variables} \n chatId {chat_id}\n")
            
            while not complete:
                messages = await websocket.recv()
                messages_json_data = json.loads(messages)
                
                for message in messages_json_data["messages"]:
                    message_payload = json.loads(message)["payload"]
                    
                    if message_payload["subscription_name"] == "messageAdded":
                        new_id = message_payload["data"]["messageAdded"]["messageId"]
                        
                        if new_id not in stored_ids:
                            if str(chat_id) in message_payload["unique_id"]:
                                text_response += message_payload["data"]["messageAdded"]["text"][idx:]
                                idx = len(message_payload["data"]["messageAdded"]["text"])
                                
                                if message_payload["data"]["messageAdded"]["state"] == "complete":
                                    complete = True
                                    
                if complete:
                    logger.warning("Response Completed!")
                    last_suggest_length = 0
                    
                    for _ in range(6):
                        messages = await websocket.recv()
                        messages_json_data = json.loads(messages)
                        message_content = json.loads(messages_json_data['messages'][0])
                        message_payload = message_content["payload"]
                        
                        if message_content["message_type"] == "subscriptionUpdate":
                            try:
                                new_suggest_length = len(message_payload["data"]["messageAdded"]["suggestedReplies"])
                                logger.info(f"Collecting suggests {new_suggest_length}/{last_suggest_length}")
                                
                                if new_suggest_length > last_suggest_length and new_suggest_length >= 1:
                                    last_suggest_length = new_suggest_length
                                    message_id = int(message_payload["data"]["messageAdded"].get("messageId", 0))
                                    time.sleep(0.5)
                                    continue
                                logger.info(f"Last Suggestions {new_suggest_length}/{last_suggest_length}")
                            except KeyError as fail:
                                logger.info(f"Key does not exist => {fail}")
                                
                    
                    stored_ids.add(message_id)
                    chat_history["message_ids"] = list(stored_ids)
                    chat_history["topic"] = variables["query"].split(" ")[:2]
                    chat_history["chat_id"] = chat_id
                    self.save_chat(token=token, chat_history=chat_history)
                    await websocket.close_transport()
                    return text_response, chat_id

    async def send_message_stream(self, request: ChatCompletionRequest, token: str = ""):
        """
        Sends a chat message to a WebSocket server via a proxy, processes the response in real-time,
        and streams the response back to the caller.

        Args:
            request (ChatCompletionRequest): An instance of ChatCompletionRequest containing the chat message and parameters.
            token (str): A string token used to identify the chat session.

        Yields:
            str: JSON-formatted response chunks containing the chat message content.
        """
        proxy = Proxy.from_url(self.proxies['uri'])
        ws_headers = self.config.WSHeaders.model_dump(by_alias=True)
        logger.info(f"Connecting via proxy URI {self.proxies['uri']}")
        
        ws_url = self.generate_ws_url()
        ws_headers["Host"] = f"{self.ws_domain}.tch.poe.com"
        
        async with proxy_connect(ws_url, extra_headers=ws_headers, proxy=proxy) as websocket:
            query, variables, gqlheaders = self.operation_builder(operation_name="message-edge")
            chat_history = self.get_chat_history(token)
            stored_ids = set(chat_history.get("message_ids", []))

            variables["query"] = request.messages[0].content[0].text
            variables["bot"] = request.model
            variables["chatId"] = chat_history.get("chat_id", "")
            variables["messagePointPrice"] = self.config.PriceMapping.get(request.model, 0)

            gql_execution_info = await self.client.execute_async(
                query=query,
                variables=variables,
                operation_name=self.config.Operations.message_edge.x_apollo_operation_name,
                headers=gqlheaders,
            )

            chat_id = gql_execution_info["data"]["messageEdgeCreate"]["chat"]["chatId"]
            idx = 0
            complete = False

            logger.warning(f"Invoking \n {variables} \n chatId {chat_id}\n")

            while not complete:
                messages = await websocket.recv()
                messages_json_data = json.loads(messages)

                for message in messages_json_data.get("messages", []):
                    message_payload = json.loads(message)["payload"]

                    if message_payload["subscription_name"] == "messageAdded":
                        new_id = message_payload["data"]["messageAdded"]["messageId"]

                        if new_id not in stored_ids:
                            if str(chat_id) in message_payload["unique_id"]:
                                chunk = {
                                    "id": chat_id,
                                    "object": "chat.completion.chunk",
                                    "created": time.time(),
                                    "model": request.model,
                                    "choices": [
                                        {
                                            "delta": {
                                                "content": message_payload["data"]["messageAdded"]["text"][idx:]
                                            }
                                        }
                                    ],
                                }
                                yield f"data: {json.dumps(chunk)}\n\n"
                                idx = len(message_payload["data"]["messageAdded"]["text"])

                                if message_payload["data"]["messageAdded"]["state"] == "complete":
                                    complete = True
                                    break

                if complete:
                    logger.warning("Response Completed!")
                    last_suggest_length = 0

                    for _ in range(6):
                        messages = await websocket.recv()
                        messages_json_data = json.loads(messages)
                        message_content = json.loads(messages_json_data['messages'][0])
                        message_payload = message_content["payload"]

                        if message_content["message_type"] == "subscriptionUpdate":
                            try:
                                new_suggest_length = len(message_payload["data"]["messageAdded"]["suggestedReplies"])
                                logger.info(f"Collecting suggests {new_suggest_length}/{last_suggest_length}")
                                
                                if new_suggest_length > last_suggest_length and new_suggest_length >= 1:
                                    last_suggest_length = new_suggest_length
                                    time.sleep(0.5)
                                    message_id = int(message_payload["data"]["messageAdded"].get("messageId", 0))
                                    continue
                                logger.info(f"Last Suggestions {new_suggest_length}/{last_suggest_length}")
                            except KeyError as fail:
                                logger.info(f"dumping... key not exist  => {fail}")

                    logger.info(f"messageId = {message_id}")
                    stored_ids.add(message_id)
                    chat_history["message_ids"] = list(stored_ids)
                    chat_history["topic"] = variables["query"].split(" ")[:2]
                    chat_history["chat_id"] = chat_id
                    self.save_chat(token=token, chat_history=chat_history)
                    await websocket.close_transport()
                    yield "data: [DONE]\n\n"
                    break

                    

    def get_available_bots(self, limit: int = 25) -> dict:
        """
        Retrieves a list of available bots from a GraphQL API.

        Args:
            limit (int): The maximum number of bots to retrieve.

        Returns:
            dict: A dictionary where keys are bot nicknames and values are their corresponding bot IDs.
        """
        payload, variables, headers = self.operation_builder("bot-pagination")
        variables["first"] = limit
        available_bots = {}
        result = self.client.execute(query=payload, variables=variables, headers=headers, operation_name=headers['x-apollo-operation-name'], proxies=self.Proxies["format"])
        for bot in result["data"]["viewer"]["availableBotsConnection"]["edges"]:
            available_bots[bot["node"]["nickname"]] = bot["node"]["botId"]

        time.sleep(2)
        return available_bots



    def chat_list(self, bot: str = "capybara", limit: int = 15) -> List[dict]:
        """
        Retrieves a list of chat summaries for a specified bot.

        Args:
            bot (str): The nickname of the bot for which to retrieve chat summaries. Default is "capybara".
            limit (int): The maximum number of chat summaries to retrieve. Default is 15.

        Returns:
            List[Dict[str, Union[str, int]]]: A list of dictionaries, each containing the chat title, ID, and brief excerpts of messages from both the human and bot participants.
        """
        logger.info(f"Sending message to {bot}: id={bot}")
        try:
            payload, variables, headers = self.operation_builder("chat-list")
            bots_map = self.get_available_bots(60)
            variables["botId"] = bots_map[bot]
            variables["first"] = limit
            message_data = self.client.execute(query=payload, variables=variables, headers=headers,
                                               operation_name=headers['x-apollo-operation-name'], proxies=self.Proxies["format"])

            chat_summaries = []
            for msg in message_data["data"]["chats"]["edges"]:
                content = {"title": msg["node"]["title"], "id": msg["node"]["chatId"]}
                for edge in msg["node"]["messagesConnection"]["edges"]:
                    if edge["node"]["authorNickname"] == "human":
                        content["human"] = edge["node"]["text"][:35] + "..."
                    else:
                        content["bot"] = edge["node"]["text"][:35] + "..."
                chat_summaries.append(content)

            return chat_summaries
        except Exception as e:
            raise e
