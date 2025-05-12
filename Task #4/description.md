🧩 FastAPI Challenge #4: Country Info API with Query Filtering

🌍 Task Description:
Create a basic API to store and filter country data.

🛠️ Requirements:
✅ Model:

Each country should have:

id: int
name: str
capital: str
population: int
✅ Endpoints:
POST /countries
➤ Add a country. Auto-assign id.
GET /countries
➤ Return all countries.
GET /countries/search
➤ Accept optional query parameters:
min_population: int
name: str (partial match, case-insensitive)
➤ Return countries that match both filters if provided.
🧪 Example Queries:
/countries/search?min_population=10000000
/countries/search?name=an
/countries/search?name=an&min_population=5000000
✅ Notes:
You can reuse your previous pattern of models and ID generation.
If no countries match, return an empty list.