from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class Greetings(BaseModel):
    name: str
    age: int

app = FastAPI()

@app.post("/greet")
def greetings(greetings: Greetings):
    if not greetings.name.strip():
        raise HTTPException(status_code=422, detail="Name cannot be empty.")
    if greetings.age < 0:
        raise HTTPException(status_code=422, detail="Age cannot be negative.")

    if greetings.age < 18:
        return {"message": f"Hello {greetings.name}! You're a minor."}
    else:
        return {"message": f"Hello {greetings.name}! You're an adult."}
