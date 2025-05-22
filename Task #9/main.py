from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Optional
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import jwt, JWTError

import jwtconfig

db = {
    "user" : {
        "username" : "user",
        "full_name" : "username",
        "hashed_password" : "$2b$12$zeg66R/BAtKcP9467kFhA.PiBWtNlhMuvshsi.3yepo4LZY7RZt/.",
        "disabled" : False,
        "budgets" : {
            "Groceries" : {
                "budget" : "Groceries",
                "limit" : 300.0,
                "purchases" : [
                    {
                        "description": "Milk and eggs",
                        "amount": 20,
                    },
                ]
            }
        }
    }
}

class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    username : Optional[str] = None

class Purchase(BaseModel):
    description : str
    amount : float

class BudgetForm(BaseModel):
    budget : str = None
    limit : float = None
    
class Budget(BudgetForm):
    purchases : list[Purchase] = Field(default_factory=list)

class UserRegistration(BaseModel):
    username : str
    password : str
    fullname : Optional[str] = None

class User(BaseModel):
    username : str = None
    full_name : Optional[str] = None
    disabled : Optional[bool] = False
    budgets : dict[str, Budget] = Field(default_factory=dict)

class UserInDB(User):
    hashed_password : str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

def verify_password(plain_password : str, hashed_password : str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password : str) -> str:
    return pwd_context.hash(password)

def get_user(db, username : str):
    if username in db:
        user_data = db[username]
        return UserInDB(**user_data)

def authenticate_user(db, username : str, password : str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False

    return user

def create_access_token(data : dict, expires_data : Optional[timedelta]):
    to_encode = data.copy()
    if expires_data:
        expire = datetime.utcnow() + expires_data
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp" : expire})
    encoded_jwt = jwt.encode(to_encode, jwtconfig.SECRET_KEY, algorithm=jwtconfig.ALGORITHM)
    return encoded_jwt

async def get_current_user(token : str = Depends(oauth2_scheme)):
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

async def get_current_active_user(current_user : UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data : OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=jwtconfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub" : user.username}, expires_data=access_token_expires)
    return {"access_token" : access_token, "token_type" : "bearer"}

@app.post("/register")
async def register_user(form : UserRegistration):
    if form.username in db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists with this username")
    
    hashed_password = get_password_hash(form.password)
    db[form.username] = {
        "username" : form.username,
        "full_name" : form.fullname,
        "hashed_password" : hashed_password,
        "budgets" : {},
        "disabled" : False,
    }

    return {"message" : "succesfully registrated"}

@app.get("/me", response_model=User)
async def read_users_me(current_user : User = Depends(get_current_active_user)):
    return current_user

@app.post("/budgets")
async def add_new_budget(new_budget : BudgetForm, current_user : User = Depends(get_current_active_user)):
    budget = new_budget.budget
    username = current_user.username
    if budget in db[username]["budgets"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Budget {budget} alrady exists")
    
    db[username]["budgets"][budget] = {
        "budget" : budget,
        "limit" : new_budget.limit,
    }   
    return {"message" : "succesfully created budget"}

@app.post("/budgets/{budget_name}/purchases")
async def add_new_purchase(budget_name : str, new_purchase : Purchase, current_user : User = Depends(get_current_active_user)):
    if budget_name not in db[current_user.username]["budgets"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Budget {budget_name} not found")
    
    db[current_user.username]["budgets"][budget_name]["purchases"].append({
        "description" : new_purchase.description, "amount" : new_purchase.amount})
    return {"message" : "succesfully created purchase"}

@app.get("/budgets/{budget_name}/status")
async def show_budget_status(budget_name : str, current_user : User = Depends(get_current_active_user)):
    if budget_name not in db[current_user.username]["budgets"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Budget {budget_name} not found")
    spent = 0
    limit = db[current_user.username]["budgets"][budget_name]["limit"]
    purchases = db[current_user.username]["budgets"][budget_name]["purchases"]
    for purchase in purchases:
        spent += purchase["amount"]

    result = {
        "budget" : budget_name,
        "limit" : limit,
        "spent" : spent,
        "remaining" : limit - spent,
    }
    if spent > limit:
        result["status"] = "OVER LIMIT"
    else:
        result["status"] = "OK"

    return result

@app.get("/budgets/overview")
async def show_users_overview(current_user: User = Depends(get_current_active_user)):
    result = []
    for budget_name in db[current_user.username]["budgets"]:
        budget_data = await show_budget_status(budget_name, current_user)
        result.append(budget_data)
    return result