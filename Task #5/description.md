🧩 FastAPI Intermediate Challenge: Full CRUD Book Manager

📚 Task Description:
Build a REST API to manage a list of books, supporting Create, Read, Update, and Delete operations.

🛠️ Book Model:
Each book should have:

id: int (auto-assigned)
title: str
author: str
year: int
✅ Required Endpoints:
POST /books
➤ Add a new book (auto-generate ID)
GET /books
➤ Return the full list of books
PUT /books/{id}
➤ Update an existing book by ID
➤ If ID doesn't exist, return 404
DELETE /books/{id}
➤ Delete a book by ID
➤ If ID doesn't exist, return 404
🧪 Notes:
Use in-memory storage (a Python list, like before).
You can reuse your Book model and add a second model with id, similar to StoredBook.
Bonus if you allow partial updates using PATCH, but that’s optional for now.