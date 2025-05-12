from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

books = {}

class Book(BaseModel):
    title : str
    author : str
    year : int

class BookUpdate(BaseModel):
    title : Optional[str] = None
    author : Optional[str] = None
    year : Optional[int] = None

@app.get("/books")
def getbooks():
    return books

@app.post("/books")
def addbook(book : Book):
    new_id = 0
    while new_id in books: new_id += 1
    books[new_id] = book
    return {"message" : f"succesfully created book with id {new_id}"}

@app.put("/books/{id}")
def updateBook(id : int, updatedBook : BookUpdate):
    if id not in books:
        raise HTTPException(status_code=404, detail="Book with that id does not exist")
    
    if updatedBook.title is not None:
        books[id].title = updatedBook.title
    if updatedBook.author is not None:
        books[id].author = updatedBook.author
    if updatedBook.year is not None:
        books[id].year = updatedBook.year
    
    return {"message" : f"succesfully updated book with id {id}"}

@app.delete("/books/{id}")
def deleteBook(id : int):
    if id not in books:
        raise HTTPException(status_code=404, detail="Book with that id does not exist")

    del books[id]
    return {"message" : f"succesfully deleted book with id {id}"}
