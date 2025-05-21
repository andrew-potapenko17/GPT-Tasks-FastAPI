from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import jwt, JWTError

import jwtconfig

db = {
    "andrew" : {
        "username" : "andrew",
        "hashed_password" : "$2b$12$KnfWVQxuIsUJayLAjiOreeLOfv2PYDv51KkcoTmja3GZFuOQdE78G",
        "notes" : {
            0 : {
                "id" : 0,
                "title" : "My First Note",
                "content" : "That is my first note",
            }
        },
        "disabled" : False,
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class NoteCreate(BaseModel):
    title: str
    content: str

class Note(NoteCreate):
    id: int

class User(BaseModel):
    username: str
    disabled: Optional[bool] = False
    notes: dict[int, Note] = Field(default_factory=dict)

class UserInDB(User):
    hashed_password: str

class RegisterUser(BaseModel):
    username : str
    password : str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

def verify_password(plain_password : str, hashed_password : str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password : str) -> str:
    return pwd_context.hash(password)

def get_user(db, username : str) -> UserInDB:
    if username not in db:
        raise HTTPException(status_code=404, detail=f"Coud not find user with username {username}")
    
    user_data = db[username]
    return UserInDB(**user_data)

def authenticate_user(db, username : str, password : str):
    user = get_user(db, username)
    if not verify_password(password, user.hashed_password):
        return False
    
    return user

def create_acces_token(data : dict, expires_delta : Optional[timedelta]):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp" : expire})
    encoded_jwt = jwt.encode(to_encode, jwtconfig.SECRET_KEY, algorithm = jwtconfig.ALGORITHM)
    return encoded_jwt

def get_current_user(token : str = Depends(oauth2_scheme)):
    credential_excpetion = HTTPException(status_code=401, detail="Coud not validate credantials")
    try: 
        payload = jwt.decode(token, jwtconfig.SECRET_KEY, algorithms=[jwtconfig.ALGORITHM])
        username : str = payload.get("sub")
        if username is None:
            raise credential_excpetion
        
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_excpetion

    user = get_user(db, username=token_data.username)
    return user

def get_current_active_user(current_user : UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive User")

    return current_user

@app.post("/token", response_model=Token)
async def login_for_acces_token(form_data : OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Coud not validate credantials")
    
    access_token_expires = timedelta(minutes=jwtconfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_acces_token(data={"sub" : user.username}, expires_delta=access_token_expires)
    return {"access_token" : access_token, "token_type" : "bearer"}

@app.post("/register")
async def register_user(registerForm : RegisterUser):
    if registerForm.username in db:
        raise HTTPException(status_code=400, detail="User already exists with this username")

    hashed_password = get_password_hash(registerForm.password)
    db[registerForm.username] = {
        "username" : registerForm.username,
        "hashed_password" : hashed_password,
        "disabled" : False,
        "notes" : {}
    }
    
    return {"message" : "succesfully registered"}

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user : User = Depends(get_current_active_user)):
    return current_user

@app.post("/addnote")
async def add_note_for_user(new_note : NoteCreate, current_user : User = Depends(get_current_active_user)):
    username = current_user.username
    noteid = len(db[username]["notes"])
    while noteid in db[username]["notes"]:
        noteid += 1
    
    db[username]["notes"][noteid] = Note(id = noteid, **dict(new_note))
    return {"message" : "succesfully created note"}

@app.delete("/deletenote/{note_id}")
async def delete_note_for_user(note_id : int, current_user : User = Depends(get_current_active_user)):
    username = current_user.username
    if note_id not in db[username]["notes"]:
        raise HTTPException(status_code=404, detail=f"Not found note with id {note_id} for user")
    
    del db[username]["notes"][note_id]
    return {"message" : "succesfully deleted note"}