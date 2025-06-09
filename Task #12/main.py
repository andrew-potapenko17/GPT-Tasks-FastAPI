# === Main File ===
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from typing import Optional
from dotenv import load_dotenv
from datetime import datetime, timedelta
from jose import jwt, JWTError
import asyncio
import os

from models import *

db = {
    "users": {},
    "global_notifications": {}
}

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


# ================== Helper Functions ===================

async def create_scheduled_notification():
    while True:
        notificationID = 0
        while notificationID in db["global_notifications"]:
            notificationID += 1
        db["global_notifications"][notificationID] = GlobalNotification(
            text="🛎️ Scheduled check-in: Remember to update your status!",
            type="global",
            id=notificationID,
        ).dict()
        print("✅ Scheduled global notification created")
        await asyncio.sleep(60)


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
    return jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
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


def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive User")
    return current_user


# ================== Routes ===================

@app.on_event("startup")
async def start_notifications_loop():
    asyncio.create_task(create_scheduled_notification())


@app.get("/")
def base_url():
    return {"header": "Notifications & Background Jobs Platform"}


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=int(os.getenv("ACCES_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/register")
async def register_new_user(form: UserRegister):
    username = form.username
    if username in db["users"]:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = get_password_hash(form.password)
    db["users"][username] = UserInDB(
        username=form.username,
        hashed_password=hashed_password,
        role=form.role,
        full_name=form.full_name,
        disabled=False,
        personal_notifications={}
    ).dict()
    return {"message": "Successfully registered"}


@app.get("/me", response_model=User)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_active_user)):
    return current_user


@app.post("/notifications/global")
async def create_global_notification(
    form: NotificationForm,
    current_user: UserInDB = Depends(get_current_active_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can send global notifications")
    notificationID = 0
    while notificationID in db["global_notifications"]:
        notificationID += 1
    db["global_notifications"][notificationID] = GlobalNotification(
        text=form.text,
        type="global",
        id=notificationID,
    ).dict()
    return {"message": "Successfully created global notification"}


@app.post("/notifications/{username}")
async def send_personal_notification(
    username: str,
    form: NotificationForm,
    current_user: UserInDB = Depends(get_current_active_user)
):
    user = get_user(db, username)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {username} not found")
    notificationID = 0
    while notificationID in user.personal_notifications:
        notificationID += 1
    user.personal_notifications[notificationID] = UserNotification(
        text=form.text,
        type="personal",
        id=notificationID,
        is_read=False
    ).dict()
    db["users"][user.username]["personal_notifications"] = user.personal_notifications
    return {"message": "Successfully created personal notification"}


@app.get("/notifications")
async def get_all_user_notifications(current_user: UserInDB = Depends(get_current_active_user)):
    notifications = []

    for notif in current_user.personal_notifications.values():
        if isinstance(notif, dict):
            notif = UserNotification(**notif)
        if not notif.is_read:
            notifications.append(notif.dict())

    for notif in db["global_notifications"].values():
        if isinstance(notif, dict):
            notif = GlobalNotification(**notif)
        notifications.append(notif.dict())

    return notifications

@app.put("/notifications/{id}/read")
async def mark_notification_as_read(id: int, current_user: UserInDB = Depends(get_current_active_user)):
    if id not in current_user.personal_notifications:
        raise HTTPException(status_code=404, detail=f"Notification ID {id} not found")
    
    notif_data = current_user.personal_notifications[id]
    if isinstance(notif_data, dict):
        notif = UserNotification(**notif_data)
    else:
        notif = notif_data
    
    notif.is_read = True
    
    current_user.personal_notifications[id] = notif.dict()
    db["users"][current_user.username]["personal_notifications"] = current_user.personal_notifications
    
    return {"message": "Marked as read"}
