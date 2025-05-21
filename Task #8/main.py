from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import Optional
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError

import jwtconfig

class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    username : Optional[str] = None

class ExpenseForm(BaseModel):
    amount : float
    category : Optional[str] = None
    description : Optional[str] = None

class Expense(ExpenseForm):
    id : int

class UpdateExpenseForm(BaseModel):
    amount : Optional[float] = None
    category : Optional[str] = None
    description : Optional[str] = None

class UserRegistration(BaseModel):
    username : str
    password : str
    fullname : Optional[str] = None

class User(BaseModel):
    username : str = None
    fullname : Optional[str] = None
    expenses : dict[int, Expense] = Field(default_factory=dict)
    disabled : Optional[bool] = False

class UserInDB(User):
    hashed_password : str

db = {}

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

def create_access_token(data : dict, expires_delta : Optional[timedelta]):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
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
    access_token = create_access_token(data={"sub" : user.username}, expires_delta=access_token_expires)
    return {"access_token" : access_token, "token_type" : "bearer"}

@app.post("/register")
async def register_user(form : UserRegistration):
    if form.username in db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists with this username")
    
    hashed_password = get_password_hash(form.password)
    db[form.username] = {
        "username" : form.username,
        "fullname" : form.fullname,
        "hashed_password" : hashed_password,
        "expenses" : {},
        "disabled" : False,
    }
    return {"message" : "succesfully registered"}

@app.get("/me", response_model=User)
async def read_users_me(current_user : User = Depends(get_current_active_user)):
    return current_user

@app.get("/expenses")
async def get_user_expenses(current_user : User = Depends(get_current_active_user)):
    return current_user.expenses

@app.post("/expenses")
async def add_new_expense(expense : ExpenseForm, current_user : User = Depends(get_current_active_user)):
    expenseID = 0
    username = current_user.username
    while expenseID in db[username]["expenses"]:
        expenseID += 1

    db[username]["expenses"][expenseID] = Expense(id=expenseID, **expense.dict())
    return {"message" : "succesfully created expense"}

@app.put("/expenses/{expense_id}")
async def update_user_expense(expense_id : int, new_expense : UpdateExpenseForm, current_user : User = Depends(get_current_active_user)):
    username = current_user.username
    if expense_id not in db[username]["expenses"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No expense with id {expense_id} for username {username}")
    
    expense_data = db[username]["expenses"][expense_id]
    if new_expense.amount is not None:
        expense_data.amount = new_expense.amount
    if new_expense.category is not None:
        expense_data.category = new_expense.category
    if new_expense.description is not None:
        expense_data.description = new_expense.description

    return {"message" : "succesfully updated expense"}

@app.delete("/expenses/{expense_id}")
async def delete_user_expense(expense_id : int, current_user : User = Depends(get_current_active_user)):
    username = current_user.username
    if expense_id not in db[username]["expenses"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No expense with id {expense_id} for username {username}")

    del db[username]["expenses"][expense_id]
    return {"message" : "succesfully deleted expense"}

@app.get("/expenses/summary")
async def summarize_user_expenses(current_user : User = Depends(get_current_active_user)):
    result = {}
    expenses = current_user.expenses
    for expense in expenses:
        if expenses[expense].category not in result:
            result[expenses[expense].category] = expenses[expense].amount
        else:
            result[expenses[expense].category] += expenses[expense].amount
    return result