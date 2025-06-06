# === Main File ===
from fastapi import FastAPI, HTTPException, status, Depends
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import jwt, JWTError

from models import *
from jwtconfig import *

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()

db = {
    "users": {},
    "messages": {},
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def get_user(db, username: str) -> Optional[UserInDB]:
    user_data = db["users"].get(username)
    if user_data:
        return UserInDB(**user_data)

def authenticate_user(db, username: str, password: str) -> Optional[UserInDB]:
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.post("/register")
async def register_new_user(form: UserRegister):
    username = form.username
    if username in db["users"]:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = get_password_hash(form.password)
    db["users"][username] = UserInDB(
        username=username,
        full_name=form.full_name,
        hashed_password=hashed_password,
        disabled=False
    ).dict()
    return {"message": "Successfully registered"}

@app.post("/messages")
async def send_message(message_form: MessageForm, current_user: User = Depends(get_current_active_user)):
    message_id = max(db["messages"].keys(), default=0) + 1
    message = Message(
        id=message_id,
        sender=current_user.username,
        receiver=message_form.receiver,
        text=message_form.text,
        is_read=False
    )
    db["messages"][message_id] = message.dict()
    return {"message": "Successfully sent message"}

@app.get("/messages/inbox")
async def get_received_messages(current_user: User = Depends(get_current_active_user)):
    username = current_user.username
    return [msg for msg in db["messages"].values() if msg["receiver"] == username]

@app.get("/messages/sent")
async def get_sent_messages(current_user: User = Depends(get_current_active_user)):
    username = current_user.username
    return [msg for msg in db["messages"].values() if msg["sender"] == username]

@app.put("/messages/{id}/read")
async def read_message(id: int, current_user: User = Depends(get_current_active_user)):
    message = db["messages"].get(id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    if message["receiver"] != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized to read this message")
    message["is_read"] = True
    return {"message": "Successfully marked as read"}
