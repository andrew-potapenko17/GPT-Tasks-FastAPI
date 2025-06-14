#
#       Models File Of FastAPI Application
#           Created: June 14 By Andrii Potapenko
#

from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token : str = None
    token_type : str = None

class TokenData(BaseModel):
    username : Optional[str] = None

class RegistrationForm(BaseModel):
    username : str = None
    password : str = None
    full_name : Optional[str] = None
    enable_2fa : Optional[bool] = False

class User(BaseModel):
    username : str = None
    full_name : Optional[str] = None
    disabled : bool = False
    enable_2fa : bool = False

class UserInDB(User):
    hashed_password : str = None

class VerifyForm(BaseModel):
    username : str = None
    code : str = None