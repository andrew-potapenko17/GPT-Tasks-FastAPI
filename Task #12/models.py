# === Models File ===
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    username : Optional[str] = None

class NotificationForm(BaseModel):
    text : Optional[str] = None
    type : Optional[str] = "personal"

class UserNotification(NotificationForm):
    id : int = None
    is_read : Optional[bool] = False

class GlobalNotification(NotificationForm):
    id : int = None

class UserRegister(BaseModel):
    username : str = None
    password : str = None
    full_name : Optional[str] = None

class User(BaseModel):
    username : str = None
    role : Optional[str] = "user"
    full_name : Optional[str] = None
    disabled : Optional[bool] = None

class UserInDB(User):
    hashed_password : str = None