⚔️ FastAPI Challenge Task #9 — Budget Battles
App Concept: Users can define budgets and log purchases. The system auto-tracks budget usage and tells them how much is left or if they’re over the limit.

📦 Features to Implement
1. Define Budget

POST /budgets
Request:

{
  "name": "Groceries",
  "limit": 300.0
}
Logic:

Store the budget under the user.
Each budget has a name, a numeric limit, and a list of purchases.
2. Add Purchase to Budget

POST /budgets/{budget_name}/purchases
Request:

{
  "description": "Milk and eggs",
  "amount": 20.0
}
Logic:

Attach this to the specified budget.
Reject if budget name doesn't exist.
3. View Budget Status

GET /budgets/{budget_name}/status
Response:

{
  "budget": "Groceries",
  "limit": 300.0,
  "spent": 95.0,
  "remaining": 205.0,
  "status": "OK"
}
Logic:

Return total spent, remaining, and "OVER LIMIT" if overspent.