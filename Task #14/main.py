#
#       Main File Of FastAPI Application
#           Created: June 14 By Andrii Potapenko
#

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from typing import Optional

from models import *


db = {
    "users" : {},
    "2fa_codes" : {}
}


app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# === Helper Functions ===


def verify_password(plain_password : str, hashed_password : str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password : str) -> str:
    return pwd_context.hash(password)


def get_user(db, username : str) -> Optional[UserInDB]:
    user_data = db["users"].get(username)
    if user_data:
        return UserInDB(**user_data)
    

def authenticate_user(db, username : str, password : str) -> UserInDB:
    user = get_user(db, username)
    if user and verify_password(password, user.hashed_password):
       return user
    

# === Routers ===


@app.get("/")
async def base_url():
    return {"headers" : "wo-Factor Authentication (2FA) System"}
