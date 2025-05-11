from fastapi import FastAPI, Query
from typing import Optional, List
from pydantic import BaseModel

app = FastAPI()

todos = []

class Todo(BaseModel):
    title: str
    completed: bool

class TodoWithID(Todo):
    id: int

@app.post("/todos")
def post_todo(todo: Todo):
    new_id = len(todos)
    new_todo = TodoWithID(id=new_id, **todo.dict())
    todos.append(new_todo)
    return {"message": "Successfully added", "todo": new_todo}

@app.get("/todos", response_model=List[TodoWithID])
def get_todos(completed: Optional[bool] = Query(None)):
    if completed is None:
        return todos
    return [todo for todo in todos if todo.completed == completed]
