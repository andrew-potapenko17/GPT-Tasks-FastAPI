✅ Task #10 – “Simple Issue Tracker API”
Domain: Project Management / Team Workflow
Logic Focus: Relationships, Status Tracking, Filtering, and Role Separation

🧠 System Concept
You're building a lightweight issue tracking system like a mini-Jira or GitHub Issues.

📂 Basic Entities
User: can be a reporter or developer
Issue:
title
description
status: "open", "in progress", "closed"
reporter: who created it
assignee: which developer is handling it
📚 API Endpoints
🔐 Auth

POST /register: register user (with role)
POST /token: login and get JWT
👤 User Info

GET /me: get current user info
🐞 Issue Management

POST /issues: create new issue (reporter only)
GET /issues: list all issues
GET /issues/{id}: get issue by ID
PUT /issues/{id}: update issue status (assignee only)
PUT /issues/{id}/assign: assign issue to a developer (admin only or self-assign)
GET /issues?status=open&assignee=username: filter issues by status, reporter, or assignee
🧩 Additional Requirements
Ensure only the reporter can edit the issue (excluding status/assignment).
Ensure only the assignee can update status.
Only a developer can be assigned to an issue.
Use in-memory DB (dictionary).
Include JWT Auth with role-based access control.