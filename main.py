from fastapi import FastAPI, Request
import uuid
from datetime import datetime, timedelta
from database import RegisterToDB, FindUserByEmail, UpdateUserByEmail

from scrapers.googlesearch import router as googlesearch_router
from scrapers.instagramprofile import router as instagramprofile_router

app = FastAPI()

app.include_router(googlesearch_router)
app.include_router(instagramprofile_router)

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
