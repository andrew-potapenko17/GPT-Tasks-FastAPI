🧠 Task #6: JWT Authentication + Account Logic

🗂️ Scenario:
You’re building a mini backend for a wallet app. Users can:

Log in and get a token
View their balance (protected route)
Deposit/withdraw money (also protected)
Prevent overdraft
🧩 Requirements
🔐 Auth (JWT)

Use a hardcoded user (username: "admin", password: "secret")
On POST to /token, return a JWT token (access token only is enough)
Use dependency injection (Depends) to decode token on each protected route
💸 Business Logic

Use an in-memory users_db = { "admin": {"password": "...", "balance": 1000} }
Implement:
Method	Path	    Description
POST	/token	    Accepts JSON with username/password, returns JWT
GET	    /me	        Returns username + current balance
POST	/deposit	Body: amount; adds to balance
POST	/withdraw	Body: amount; subtracts if enough, else 400