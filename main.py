from fastapi import FastAPI, Request
import uuid
from datetime import datetime, timedelta

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
    
    if email in userDB:
        return {"message": "User already exists"}
    
    plan_name = "free"
    credits = plans[plan_name]['credits']
    apikey = str(uuid.uuid4())
    expiry = (datetime.utcnow() + timedelta(days=30)).isoformat()

    userDB[email] = {
        "fullname": fullname,
        "email": email,
        "password": password,
        "plan": plan_name,
        "credits": credits,
        "apikey": apikey,
        "expiry": expiry
    }

    user = userDB[email]

    return {"message": "User registered successfully", "user": user}


@app.post("/dashboard")
async def dashboard(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return {"message": "All fields are required"}
    
    user = userDB.get(email)
    if not user or user['password'] != password:
        return {"message": "Invalid credentials"}

    user_data = user.copy()
    user_data.pop("password")

    return {"message": "User logged in successfully", "user": user_data}


@app.get("/buy")
async def buy(email: str, plan_name: str):
    if plan_name not in plans:
        return {"message": "Invalid Plan"}

    if email not in userDB:
        return {"message": "User not found"}

    if plan_name == "free":
        return {"message": "Free plan is already activated"}

    user = userDB.get(email)

    #TODO - Implement Payment Gateway Integration

    user['plan'] = plan_name
    user['credits'] = plans[plan_name]['credits']
    user['expiry'] = (datetime.utcnow() + timedelta(days=30)).isoformat()

    user_data = user.copy()
    user_data.pop("password")

    return {"message": "Plan Upgraded Successfully", "user": user_data} 