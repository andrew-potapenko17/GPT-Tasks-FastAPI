from fastapi import FastAPI, Query
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

class Book(BaseModel):
    title : str
    author : str

class StoredBook(Book):
    id : int

books = []

@app.get("/books")
def getbooks():
    return books

@app.get("/books/search")
def booksearch(title: Optional[str] = Query(None), author: Optional[str] = Query(None)):
    if title == None and author == None:
        return {"error" : "query params are missing"}
    if title != None and author != None:
        return {"error" : "too much params"}
    query_books = []
    title = title.lower()
    author = author.lower()
    if title != None:
        for book in books:
            if title in book.title.lower():
                query_books.append(book)
    elif author != None:
        for book in books:
            if author in book.author.lower():
                query_books.append(book)
    return query_books


@app.post("/books")
def addbook(book : Book):
    new_id = len(books)
    new_book = StoredBook(id = new_id, **book.dict())
    books.append(new_book)
    return {"message" : "succesfully added new book"}
