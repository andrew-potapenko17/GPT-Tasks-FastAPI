# === Models File ===
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    username : Optional[str] = None

class UserRegister(BaseModel):
    username : str = None
    password : str = None
    full_name : Optional[str] = None

class User(BaseModel):
    username : str = None
    full_name : Optional[str] = None
    disabled : Optional[bool] = False

class UserInDB(User):
    hashed_password : str = None

class MessageForm(BaseModel):
    receiver : str
    text : str

class Message(MessageForm):
    id : int
    sender : str
    is_read : Optional[bool] = False

        
    
        
    
