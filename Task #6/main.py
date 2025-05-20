from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
import jwtconfig

users_db = {
    "admin" : {
        "username" : "admin",
        "hashed_password" : "$2b$12$2v7bSQVBc1YLDZsEgrN9fufc2oPMtSjyFhnhVIkZSPV4ipOKiXODW",
        "balance" : 1000,
    }
}

class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    username : Optional[str] = None

class User(BaseModel):
    username : str = None
    balance : int = None

class UserInDB(User):
    hashed_password : str

class MoneyForm(BaseModel):
    money : int = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

def verify_password(plain_password : str, hashed_password : str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password : str):
    return pwd_context.hash(password)

def get_user(db, username : str):
    if username not in db:
        raise HTTPException(status_code=404, detail=f"There is no user with username {username}")
    user_data = db[username]
    return UserInDB(**user_data)

def authenticate_user(db, username : str, password : str):
    user = get_user(db, username)
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_acces_token(data : dict):
    encoded_jwt = jwt.encode(data, jwtconfig.SECRET_KEY, algorithm = jwtconfig.ALGORITHM)
    return encoded_jwt

async def get_current_user(token : str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=401, detail="Could not authenticate")
    try:
        payload = jwt.decode(token, jwtconfig.SECRET_KEY, algorithms = jwtconfig.ALGORITHM)
        username : str = payload.get("sub")
        if username is None:
            raise credential_exception
        
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception
    
    user = get_user(users_db, username=token_data.username)
    return user

@app.post("/token", response_model=Token)
async def login_for_acces_token(form_data : OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(users_db, form_data.username, form_data.password)
    access_token = create_acces_token(data={"sub" : user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model = User)
async def read_users_me(current_user : User = Depends(get_current_user)):
    return current_user

@app.post("/deposit")
async def deposit_money(moneyForm : MoneyForm, current_user : User = Depends(get_current_user)):
    if not moneyForm.money:
        raise HTTPException(status_code=400, detail = "Not provided money amount")
    
    username = current_user.username
    users_db[username]["balance"] += moneyForm.money
    return {"message" : "succesfully deposited"}

@app.post("/withdraw")
async def withdraw_money(moneyForm : MoneyForm, current_user : User = Depends(get_current_user)):
    if not moneyForm.money:
        raise HTTPException(status_code=400, detail = "Not provided money amount")
    username = current_user.username

    if moneyForm.money > users_db[username]["balance"]:
        raise HTTPException(status_code=400, detail = "Not enough funds")
    users_db[username]["balance"] -= moneyForm.money
    return {"message" : "succesfully withdrawn"}

