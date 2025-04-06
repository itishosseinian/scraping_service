from fastapi import FastAPI, Request
import uuid
from datetime import datetime, timedelta
import httpx
from database import RegisterToDB, FindUserByEmail, FindUserByAPIKey, UpdateUserByEmail, DecreaseBlance


app = FastAPI()

plans = {
    "free": {"credits": 100, "price": 0, "description": "Free plan with 100 credits"},
    "basic": {"credits": 1000, "price": 10, "description": "Basic plan with 1000 credits"},
    "pro": {"credits": 10000, "price": 100, "description": "Pro plan with 10000 credits"}
}

userDB = {}

@app.get("/")
async def root():
    return {"message": "Hello Programmers! Codemate Tv is here"}

@app.get("/pricing")
async def pricing():
    return {"plans": plans}

@app.post("/register")
async def register(request: Request):
    data = await request.json()
    fullname = data.get("fullname")
    email = data.get("email")
    password = data.get("password")

    if not all([fullname, email, password]):
        return {"message": "All fields are required"}
    
    existing_user = await FindUserByEmail(email)

    if existing_user:
        return {"message": "User already exists"}
    
    plan_name = "free"
    credits = plans[plan_name]['credits']
    apikey = str(uuid.uuid4())
    expiry = (datetime.utcnow() + timedelta(days=30)).isoformat()

    userdata = {
        "fullname": fullname,
        "email": email,
        "password": password,
        "plan": plan_name,
        "credits": credits,
        "apikey": apikey,
        "expiry": expiry
    }

    await RegisterToDB(userdata)

    return {"message": "User registered successfully"}


@app.post("/dashboard")
async def dashboard(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return {"message": "All fields are required"}
    
    user = await FindUserByEmail(email)

    if not user or user['password'] != password:
        return {"message": "Invalid credentials"}

    user.pop("_id", None)  # Remove the MongoDB ObjectId field if present

    return {"message": "User logged in successfully", "user": user}


@app.get("/buy")
async def buy(email: str, plan_name: str):
    if plan_name not in plans:
        return {"message": "Invalid Plan"}

    existing_user = await FindUserByEmail(email)
    if not existing_user:
        return {"message": "User not found"}

    if plan_name == "free":
        return {"message": "Free plan is already activated"}

    #TODO - Implement Payment Gateway Integration


    plan_credits = plans[plan_name]['credits']
    plan_expiry = (datetime.utcnow() + timedelta(days=30)).isoformat()

    await UpdateUserByEmail(email, plan_name, plan_credits, plan_expiry)

    return {"message": "Plan Upgraded Successfully"} 


@app.post("/scrapers")
async def scraper(request: Request):
    cost = 1 # Cost per scrape

    header = request.headers
    userkey = header.get("apikey")

    if not userkey:
        return {"message": "API key is missing"}

    user = await FindUserByAPIKey(userkey)
    if not user:
        return {"message": "Invalid API key"}

    if user['credits'] < cost:
        return {"message": "Insufficient credits"}

    data = await request.json()
    keyword = data.get("keyword")

    url = "https://api.scrapeasap.com/scrapers/google_search"

    payload = {
        "query": keyword,
        "page": 1,
        "limit": 10
    }
    
    headers = {
        "apikey": "b3fe812f7bb9b010fec567deeace9b9dd15d8a74a020440adc741a97ac147cc1",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:

        response = await client.post(url, json=payload, headers=headers, timeout=30.0)
    
    await DecreaseBlance(userkey, cost)

    return{"scraped data": response.text}

