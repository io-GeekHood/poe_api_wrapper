import json
from pydantic import BaseModel, Field,computed_field
from typing import Dict, List, Optional, Literal
# from assets.config import WS_HEADERS, HEADERS, COOKIES, OPERATIONS, WS_CHANNEL
import yaml
import os
class Proxies(BaseModel):
    type: str = Field(alias="Type")
    host: str = Field(alias="Host")
    port: int = Field(alias="Port")
    @computed_field
    @property
    def uri(self) -> str:
        return f"http://{self.host}:{self.port}"
    
    @computed_field
    @property
    def format(self) -> str:
        return {"https": self.uri, "http": self.uri}




class WSChannel(BaseModel):
    channel: str = Field(alias="channel")
    wss_key: str = Field(alias="wss-key")


class WSHeaders(BaseModel):
    upgrade: str = Field(alias="Upgrade")
    connection: str = Field(alias="Connection")
    sec_webSocket_version: str = Field(alias="Sec-WebSocket-Version")
    sec_webSocket_key:str = Field(alias="Sec-WebSocket-Key")
    user_agent: str = Field(alias="User-Agent")
    accept_encoding: str = Field(alias="Accept-Encoding")
    host: Optional[str] = Field(alias="Host", default=None)


class Cookies(BaseModel):
    m_s: str = Field(alias="m-s")
    m_uid: int = Field(alias="m-uid")
    m_login: int = Field(alias="m-login")
    m_b: str = Field(alias="m-b")
    m_b_lax: str = Field(alias="m-b_lax")
    m_b_strict: str = Field(alias="m-b_strict")
    m_lat: str = Field(alias="m-lat")


class Headers(BaseModel):
    accept: str
    quora_formkey: str = Field(alias="quora-formkey")
    quora_tchannel: str = Field(alias="quora-tchannel")
    user_agent: str = Field(alias="user-agent")
    poe_language_code: str = Field(alias="poe-language-code")
    content_type: str = Field(alias="content-type")
    cookie: str = Field(alias="cookie")

class Operation(BaseModel):
    x_apollo_operation_name: str = Field(..., alias="x-apollo-operation-name")
    x_apollo_operation_id: str = Field(..., alias="x-apollo-operation-id")


class Operations(BaseModel):
    bot_pagination: Operation = Field(..., alias="bot-pagination")
    message_edge: Operation = Field(..., alias="message-edge")
    bot_query: Operation = Field(..., alias="bot-query")
    chat_pagination: Operation = Field(..., alias="chat-pagination")
    chat_list: Operation = Field(..., alias="chat-list")
    bots_explore: Operation = Field(..., alias="bots-explore")
    subscription: Operation

class Price_Mapping(BaseModel):
    gpt4_o:int=300
    capybara:int=20
    beaver:int= 350 
    llama38b:int=15 
    gemini_pr:int=20
    dalle3:int=1500
    upstage_solar_0_70b_16:int=1
    stablediffusion:int=80
    playgroundv:int=40
    websear:int=40
    claude_2_1_bambo:int=200
    claude_3_hai:int=30
    claude_2_1_cedar:int=2000
    gemini_1_5_pr:int=250
    stablediffusion3:int=1600
    sd3turbo:int=1000

class PoeConfig(BaseModel):
    WSChannel: WSChannel
    SettingsUrl: str = ""
    PriceMapping: dict = {}
    GqlUri: str = ""
    WSHeaders: WSHeaders
    Cookies: Cookies
    Headers: Headers
    Operations: Operations
    Proxies: Proxies
    def __init__(self, config_file_path:str) -> None:
        self.load_config(config_file_path)
        self.Headers.cookie = self.cookies_string_formatted()
        self.SettingsUrl = f"https://poe.com/api/settings?channel={self.WSChannel.channel}"
        self.PriceMapping = Price_Mapping().model_dump()
        self.GqlUri = "https://www.quora.com/poe_api/gql_POST"
        self.WSHeaders.sec_webSocket_key = self.WSChannel.wss_key
    def load_config(self,config_file_path:str):
        with open(config_file_path, 'r') as yaml_in:
            yaml_object = yaml.safe_load(yaml_in)
        super().__init__(**yaml_object)
    def get_bot_price(self,botname:str) -> Dict:
        return self.PriceMapping[botname]
    def headers_without_cookies(self) -> Dict:
        model_dump = self.Headers.model_dump(by_alias=True)
        model_dump_none_removed = {}
        for k, v in model_dump.items():
            if v is not None:
                model_dump_none_removed[k] = v
        return model_dump_none_removed

    def cookies_string_formatted(self) -> str:
        formatted_pairs = []
        for key, value in self.Cookies.model_dump(by_alias=True).items():
            formatted_pairs.append(f"{key}={value}")
        result_string = "; ".join(formatted_pairs)
        return result_string

class ContentFormat(BaseModel):
    type: str= "text"
    text: str= ""
class Message(BaseModel):
    role: str
    content: List[ContentFormat]

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "mock-gpt-model"
    messages: List[Message]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.1
    stream: Optional[bool] = False

class OpenAiRequest(BaseModel):
    token:str=""
    request:ChatCompletionRequest


class Api_Metrics(BaseModel):
    host: str = '0.0.0.0'
    port: int = 5526
    num_workers: int = 4
    version: str = 'v2'
    loglevel:str = "info"

# poe_config = PoeConfig.model_validate(
#     {
#         "ws_channel": WS_CHANNEL,
#         "ws_headers": WS_HEADERS,
#         "cookies": COOKIES,
#         "headers": HEADERS,
#         "operations": OPERATIONS,
#     }
# )

