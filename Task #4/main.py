from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

countries = []

class Country(BaseModel):
    name : str
    capital : str
    population : int

class StoredCountry(Country):
    id : int

@app.get("/countries")
def getcountries():
    return countries

@app.get("/countries/search")
def querycountries(min_population: Optional[int] = Query(None), name: Optional[str] = Query(None)):
    if min_population is None and name is None:
        raise HTTPException(status_code=400, detail="At least one query parameter required")
    response_countries = []
    for country in countries:
        if min_population is not None and country.population < min_population:
            continue
        if name is not None and (name.lower() not in country.name.lower()):
            continue
        response_countries.append(country)
    return response_countries

@app.post("/countries")
def postcountry(country : Country):
    new_id = len(countries)
    new_country = StoredCountry(id = new_id, **country.dict())
    countries.append(new_country)
    return {"message" : "succesfully created new country"}