🚀 FastAPI Challenge — Task #12: Notifications & Background Jobs
🧩 Concept:
Build a user notification system that supports:

System-wide announcements (e.g., “Server maintenance at 2 AM”)
User-specific notifications (e.g., “Your profile was viewed 5 times today”)
Background job to simulate scheduled notifications every X seconds
📜 Requirements
✅ Endpoints

POST /notifications/global
Create a global notification (admin only).
All users will see this in their /notifications inbox.
POST /notifications/user
Send a direct notification to a specific user.
GET /notifications
Returns the current user's unread notifications (global + personal).
You can store a read: false field per notification.
PUT /notifications/{id}/read
Mark a specific notification as read.
⚙️ Background Job

On startup, launch a background task that:
Every 60 seconds, creates a global notification like:
"🛎️ Scheduled check-in: Remember to update your status!"
🔐 Auth Rules

Only an admin user can post global notifications.
Any user can:
Get their own notifications
Mark them as read
Send direct notifications (if you want to simulate that)