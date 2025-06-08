from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from typing import Optional

from models import *

db = {
    "users" : {},
    "global_notifications" : {}
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

def verify_password(plain_password : str, hashed_password : str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password : str):
    return pwd_context.hash(password)

def get_user(db, username : str) -> Optional[UserInDB]:
    user_data = db["users"].get(username)
    if (user_data):
        return UserInDB(**user_data)

def authenticate_user(db, username : str, password : str) -> Optional[UserInDB]:
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

@app.get("/")
def base_url():
    return {"header" : "Notifications & Background Jobs Platform"}

