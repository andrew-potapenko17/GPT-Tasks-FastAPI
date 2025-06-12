#
#       Main File Of FastAPI Application
#           Created: June 12 By Andrii Potapenko
#

from fastapi import FastAPI, HTTPException, status, UploadFile, Depends, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from passlib.context import CryptContext
from typing import Optional
from jose import jwt, JWTError
from dotenv import load_dotenv
from datetime import datetime, timedelta
from uuid import uuid4
from io import BytesIO
import os

from models import *

load_dotenv()

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

db = {
    "users" : {},
    "files" : {},
}

# ==== Helper Functions ==== 


def verify_password(plain_password : str, hashed_password : str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password : str) -> str:
    return pwd_context.hash(password)


def get_user(db, username : str) -> Optional[UserInDB]:
    user_data = db["users"].get(username)
    if user_data:
        return UserInDB(**user_data)


def authenticate_user(db, username : str, password : str) -> Optional[UserInDB]:
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


# ==== Routers ====


@app.get("/")
async def base_url():
    return {"headers" : "File Sharing System"}


@app.post("/token", response_model=Token)
async def login_for_acccess_token(form_data : OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=int(os.getenv("EXACCES_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(
        data={"sub" : user.username}, expires_delta=access_token_expires
    )
    return {"access_token" : access_token, "token_type" : "bearer"}


@app.post("/register")
async def register_new_user(form : RegistrationForm):
    username = form.username
    if username in db["users"]:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = get_password_hash(form.password)
    db["users"][username] = UserInDB(
        username=form.username,
        hashed_password=hashed_password,
        full_name=form.full_name,
        disabled=False
    ).dict()
    return {"message": "Successfully registered"}


@app.get("/me", response_model=User)
async def get_current_user_info(current_user : UserInDB = Depends(get_current_active_user)):
    return current_user


@app.get("/files/me")
async def get_user_files(current_user : UserInDB = Depends(get_current_active_user)):
    result = []
    for file_entry in db["files"].values():
        if file_entry["author"] == current_user.username:
            result.append(file_entry)
    return result


@app.post("/files/upload")
async def upload_new_file(file : UploadFile, current_user : UserInDB = Depends(get_current_active_user)):
    file_uuid = str(uuid4())
    content = await file.read()
    db["files"][file_uuid] = File(
        uuid=file_uuid,
        author=current_user.username,
        filename=file.filename,
        content=content,
        downloaded=False,
    ).dict()
    return {
        "uuid": file_uuid,
        "download_link": f"/files/download/{file_uuid}"
    }


@app.put("/files/download/{file_uuid}")
async def download_file(file_uuid : str):
    file_entry = db["files"].get(file_uuid)
    if not file_entry:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    file = File(**file_entry)
    if file.downloaded:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="File was already downloaded"
        )
    file.downloaded = True
    db["files"][file.uuid] = file.dict()
    return StreamingResponse(
        BytesIO(file.content),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{file.filename}"'}
    )
