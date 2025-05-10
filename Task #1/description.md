🧩 FastAPI Challenge #1: Basic User API

🚀 Task Description:
Create a simple FastAPI application with a single endpoint that allows users to submit their name and age via a POST request, and returns a greeting message based on their age.

🛠️ Requirements:
Endpoint: POST /greet
Request Body (JSON):

{
  "name": "Alice",
  "age": 25
}s

Response (JSON):

If age < 18:
{
  "message": "Hello Alice! You're a minor."
}

If age >= 18:
{s
  "message": "Hello Alice! You're an adult."
}

✅ Return a 422 error if name is empty or age is negative.