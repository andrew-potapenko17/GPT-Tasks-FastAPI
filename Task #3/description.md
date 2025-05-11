🧩 FastAPI Challenge #3 (New Task): Book Search API

📚 Task Description:
Build a basic API to manage and search for books by title and author.

🛠️ Requirements:
✅ Model:

Each book should have:

id: int
title: str
author: str
✅ Endpoints:
POST /books
➤ Add a new book. Auto-assign an ID.
GET /books
➤ Return all books.
GET /books/search
➤ Accept optional query parameters:
title: string (e.g. /books/search?title=harry)
author: string (e.g. /books/search?author=rowling)
➤ Return books that match either (case-insensitive partial match).
🧪 Example Search:
GET /books/search?title=stone
Would return:

[
  {
    "id": 0,
    "title": "Harry Potter and the Sorcerer's Stone",
    "author": "J.K. Rowling"
  }
]