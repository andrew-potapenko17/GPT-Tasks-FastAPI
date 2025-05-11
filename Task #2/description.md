🧩 FastAPI Challenge #2: Todo API with Query Filtering

🚀 Task Description:
Build a small Todo API with in-memory storage and query parameter filtering.

🛠️ Requirements:
Model:
Each todo item has:
id: int
title: str
completed: bool
Endpoints:
POST /todos
➤ Add a new todo item. Assign id automatically.
GET /todos
➤ Return the list of todos. If completed=true or false is passed as a query parameter, return only filtered items.
📥 Sample Request:
POST /todos

{
  "title": "Buy milk",
  "completed": false
}
GET /todos

GET /todos → return all todos
GET /todos?completed=true → return only completed todos
✅ Notes:
You can use a simple list to store todos in memory (todos = []).
Autoincrement the ID (e.g., keep a counter or use len(todos) + 1).
Use Optional[bool] for the query parameter in the GET route.