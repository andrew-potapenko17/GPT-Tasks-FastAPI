#
#       Main File Of FastAPI Application
#           Created: June 14 By Andrii Potapenko
#

from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from typing import Optional
from jose import jwt, JWTError

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

def create_access_token(data : dict, expires_delta : Optional[timedelta]):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp" : expire})
    return jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm = os.getenv("ALGORITHM"))


def get_current_user(token : str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validtsate credentials"
    )
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms = [os.getenv("ALGORITHM")])
        username : str = payload.get("sub")
        if username is None:
            raise credentials_exception
        tokenData = TokenData(username = username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username = tokenData.username)
    if user is None:
        raise HTTPException
    return user


def get_current_active_user(current_user : UserInDB = Depends(get_current_user)) -> UserInDB:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive User")
    return current_user


# === Routers ===


@app.get("/")
async def base_url():
    return {"headers" : "wo-Factor Authentication (2FA) System"}
