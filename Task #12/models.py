# === Models File ===
from pydantic import BaseModel, Field
from typing import Optional

class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    username : Optional[str] = None

class NotificationForm(BaseModel):
    text : Optional[str] = None
    
class UserNotification(NotificationForm):
    id : int = None
    is_read : Optional[bool] = False
    type : Optional[str] = "personal"

class GlobalNotification(NotificationForm):
    id : int = None
    type : Optional[str] = "global"

class UserRegister(BaseModel):
    username : str = None
    password : str = None
    role : Optional[str] = "user"
    full_name : Optional[str] = None

class User(BaseModel):
    username : str = None
    role : Optional[str] = "user"
    full_name : Optional[str] = None
    disabled : Optional[bool] = None
    personal_notifications : dict[int, UserNotification] = Field(default_factory=dict)

class UserInDB(User):
    hashed_password : str = None