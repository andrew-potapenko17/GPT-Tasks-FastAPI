from fastapi import FastAPI, HTTPException, status, Depends, Query
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import jwt, JWTError

import jwtconfig

class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    username : Optional[str] = None

class UserRegister(BaseModel):
    username : str = None
    password : str = None
    full_name : Optional[str] = None
    role : str

class User(BaseModel):
    username : str = None
    full_name : Optional[str] = None
    role : str = None
    disabled : Optional[bool] = False

class UserInDB(User):
    hashed_password : str

class UpdateIssue(BaseModel):
    status : str = None

class AssignIssue(BaseModel):
    assignee : str = None

class IssueForm(BaseModel):
    title : str
    description : Optional[str] = None
    assigne : Optional[str] = None
    
class Issue(BaseModel):
    id : int
    reporter : str
    status : Optional[str] = None

db = {
    "users": {
        "alice": {
            "username": "alice",
            "full_name": "Alice Reporter",
            "hashed_password": "$2b$12$jyXlAckHk7q5KTD0zWMzEudKM10g7tyhaW/JKJnaZ/xZzZZYwrRBa",
            "role": "reporter",
            "disabled": False,
        },
        "bob": {
            "username": "bob",
            "full_name": "Bob Developer",
            "hashed_password": "$2b$12$jyXlAckHk7q5KTD0zWMzEudKM10g7tyhaW/JKJnaZ/xZzZZYwrRBa",
            "role": "developer",
            "disabled": False,
        }
    },
    "issues": {
        1: {
            "id": 1,
            "title": "Bug in login page",
            "description": "Login button doesn’t work on mobile.",
            "status": "open",
            "reporter": "alice",
            "assignee": "bob",
        },
        2: {
            "id": 2,
            "title": "Typo in homepage header",
            "description": "Header says 'Welcom' instead of 'Welcome'.",
            "status": "open",
            "reporter": "alice",
            "assignee": None,
        }
    }
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

def verify_password(plain_password : str, hashed_password : str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password : str) -> str:
    return pwd_context.hash(password)

def get_user(db, username : str) -> UserInDB:
    if username in db["users"]:
        user_data = db["users"][username]
        return UserInDB(**user_data)
    
def authenticate_user(db, username : str, password : str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    
    return user

def create_access_token(data : dict, expires_delta : Optional[timedelta]):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp" : expire})
    encoded_jwt = jwt.encode(to_encode, jwtconfig.SECRET_KEY, algorithm=jwtconfig.ALGORITHM)
    return encoded_jwt

def get_current_user(token : str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, jwtconfig.SECRET_KEY, algorithms=[jwtconfig.ALGORITHM])
        username : str = payload.get("sub")
        if username is None:
            raise credential_exception
        
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception
    
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credential_exception
    
    return user

def get_current_active_user(current_user : UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data : OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=jwtconfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub" : user.username}, expires_delta=access_token_expires)
    return {"access_token" : access_token, "token_type" : "bearer"}

@app.get("/me", response_model=User)
async def read_users_me(current_user : User = Depends(get_current_active_user)):
    return current_user

@app.post("/register")
async def register_new_user(form : UserRegister):
    username = form.username
    if username in db["users"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists with this username")
    
    if form.role not in ["reporter", "developer", "admin"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect role that given to user")

    hashed_password = get_password_hash(form.password)
    db["users"][username] = {
        "username" : username,
        "full_name" : form.full_name,
        "hashed_password" : hashed_password,
        "role" : form.role,
        "disabled" : False,
    }

    return {"message" : "succesfully registrated"}

@app.post("/issues")
async def create_new_issue(form : IssueForm, current_user : User = Depends(get_current_active_user)):
    if current_user.role != "reporter":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User needs to be reporter for this")
    
    issueID = 0
    while issueID in db["issues"]:
        issueID += 1
    
    db["issues"][issueID] = {
        "id" : issueID,
        "title": form.title,
        "description": form.description,
        "status": "open",
        "reporter": current_user.username,
        "assignee": form.assigne,
    }

    return {"message" : "succesfully added issue"}

@app.get("/issues")
async def get_all_issues(status: Optional[str] = Query(None), reporter: Optional[str] = Query(None), assignee: Optional[str] = Query(None)):
    issues = db["issues"]
    result = []
    for issue in issues:
        if status is not None and issue["status"] != status:
            continue
        if reporter is not None and issue["reporter"] != reporter:
            continue
        if assignee is not None and issue["assignee"] != assignee:
            continue
        result.append(issue)
    return result

@app.get("/issues/{id}")
async def get_issue_by_id(id : int):
    if id not in db["issues"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Not found isssue with id {id}")
    
    return db["issues"][id]

@app.put("/issues/{id}")
async def update_issue_status(id : int, form : UpdateIssue, current_user : User = Depends(get_current_active_user)):
    if id not in db["issues"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Not found isssue with id {id}")
    
    if db["issues"][id]["assignee"] != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not allowed to edit this")
    
    db["issues"][id]["status"] = form.status
    return {"message" : "succesfully updated status"}

@app.put("/issues/{id}/assign")
async def assign_issue(id : int, form : Optional[AssignIssue] = None, current_user : User = Depends(get_current_active_user)):
    if id not in db["issues"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Not found isssue with id {id}")
    
    if form is not None and current_user.role == "admin":
        if form.assignee in db["users"] and db["users"][form.assignee]["role"] == "developer":
            db["issues"][id]["assignee"] = form.assignee
            return {"message" : "succesfully updated assignee"}
    else:
        if current_user.role == "developer" and db["issues"][id]["assignee"] == None:
            db["issues"][id]["assignee"] = current_user.username
            return {"message" : "succesfully updated assignee"}
        
    raise HTTPException(status_code=status.HTTP400, detail=f"Issue with user request")
    

