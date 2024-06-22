from pydantic import BaseModel
from typing import Union, List,Dict

# this type enforces api response fields
class sock_connect_response(BaseModel):
    success: bool = False
    exception: Union[str, None] = None
    result: Dict
class chat_query(BaseModel):
    text: str = ""
    chatId: Union[int, None] = None
    chatBot: Union[str, None] = None

class list_query(BaseModel):
    chatBot: Union[str, None] = None
    limit: Union[int, None] = None

