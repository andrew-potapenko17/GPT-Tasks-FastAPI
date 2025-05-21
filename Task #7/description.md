🧠 Task #7 (Alt): JWT-Protected Notes App

🗂️ Scenario:
Build a personal notes backend where each authenticated user can:

Create notes
View all of their notes
Delete a note by ID
No one can see another user’s notes
🔐 Authentication
You’ll still use:

POST /register — register a user
POST /token — login to get JWT
Use Depends(get_current_user) to secure routes
🧾 Notes Data Model
Each user has a list of their notes.

notes_db = {
  "username1": [
    {"id": 0, "title": "Note A", "content": "..." },
    {"id": 1, "title": "Note B", "content": "..." }
  ],
  ...
}
✅ Required Endpoints
Method	Route	Description
POST	/register	Create new user
POST	/token	    Login and receive JWT token
GET	    /notes	    Get all notes for current user
POST	/notes	    Add a new note
DELETE	/notes/{id}	Delete a note owned by current user