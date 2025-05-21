🧩 Task #8 — Expense Tracker App (JWT-Protected)

You're building a personal finance manager. Each user can add, update, delete, and list their expenses. Every operation is secured with JWT.

📌 Requirements
✅ Models

User: Same as before.
Expense:
id: int
amount: float
category: str (e.g., "food", "transport", "rent")
timestamp: datetime (use datetime.utcnow() by default)
description: Optional[str]
✅ Features

Register new users
Login users and return a JWT token
Authenticated users can:
📌 POST /expenses – Add new expense
📌 GET /expenses – Get all expenses
📌 PUT /expenses/{id} – Update a specific expense
📌 DELETE /expenses/{id} – Delete a specific expense
📌 GET /expenses/summary – Get total spent per category
🔒 Auth
Use the same JWT logic you already built (reuse from Task #7).
Only authenticated users can manage their expenses.
🧠 Business Logic
Summary endpoint:
Return a dict like:
{
  "food": 150.50,
  "rent": 450.00,
  "transport": 75.00
}
This requires you to iterate over user's expenses and group by category.