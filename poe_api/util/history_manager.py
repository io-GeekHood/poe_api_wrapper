import json
# from poe_api.util.logging import logger

class HistoryManager:
    filepath:str = "assets/chats.json"
    test:str
    @classmethod
    def save_chat(cls,token:str,chat_history:dict):
        with open(cls.filepath,"r") as chats_file:
            chats = json.load(chats_file)
            chats[token] = chat_history 
        with open("assets/chats.json","w") as chats_file:
            json.dump(chats,chats_file,indent=4,ensure_ascii=False)
                        

    @classmethod
    def get_chat_history(cls,token:str):
        with open(cls.filepath,"r") as chats_file:
            chats = json.load(chats_file)
            return chats.get(token,{"message_ids":[],"topic":"","chat_id":None})

    @classmethod
    def update_history(cls,chat_history:dict={}) -> None:
        with open(cls.filepath,"r") as chats_file:
            chats = json.load(chats_file)
            for chat in chats:
                if chat["token"] == chat_history['token']:
                    return
