🔥 FastAPI Challenge Task #11 — "Secure ChatRoom API" (Level 2 Difficulty)
Goal: Build a lightweight internal messaging system (chatroom-style) where only authenticated users can send, receive, and fetch messages. Completely different logic from Task 10 (no issues, no roles).

🧠 Concept
Each user can:

Send a message to another user.
Fetch all received messages.
Fetch all sent messages.
Mark a message as "read".
Each message has:

id, sender, receiver, text, timestamp, is_read.
📄 Endpoints
Method	Path	Auth	Description
POST	/register	❌	Register a new user.
POST	/token	❌	Login, returns JWT.
POST	/messages	✅	Send a message to another user.
GET	    /messages/inbox	✅	Get all messages received by the current user.
GET     /messages/sent	✅	Get all messages sent by the current user.
PUT   	/messages/{id}/read	✅	Mark message as read (receiver only).
✅ Requirements
Only logged-in users can send/receive messages.
A message should have:
id (int, autoincrement)
sender (str)
receiver (str)
text (str)
timestamp (datetime)
is_read (bool)
Messages must be stored in memory (db["messages"] = {}).
Only receiver can mark message as read.
No user roles required.
🔐 JWT
Keep your JWT system as-is.
No roles — any user can send/receive.
💡 Bonus (optional if you want to go harder)
Add a delete endpoint to let a sender delete their sent message.
Add a search parameter (e.g. /messages/inbox?text=hi) to filter messages.