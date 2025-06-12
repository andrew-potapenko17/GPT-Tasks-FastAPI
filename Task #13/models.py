#
#       Models File Of FastAPI Application
#           Created: June 12 By Andrii Potapenko
#

from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token : str = None
    token_type : str = None

class TokenData(BaseModel):
    username : Optional[str] = None

class RegistrationForm(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None

class User(BaseModel):
    username : str = None
    full_name : Optional[str] = None
    disabled : Optional[bool] = False

class UserInDB(User):
    hashed_password : str = None

class File(BaseModel):
    uuid : str = None
    author : Optional[str] = None
    filename : Optional[str] = None
    content : bytes = None
    downloaded : Optional[bool] = False