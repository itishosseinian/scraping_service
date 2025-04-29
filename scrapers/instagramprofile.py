from fastapi import Request, APIRouter
from database import FindUserByAPIKey, DecreaseBlance
import httpx

from dotenv import load_dotenv
import os

load_dotenv()

SCRAPEASAP_KEY = os.getenv("SCRAPEASAP_KEY")


router = APIRouter(prefix="/scrapers")

@router.post("/instagramprofile")
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


    username = data.get("username")

    url = "https://api.scrapeasap.com/scrapers/instagram_user_profile"

    payload = {
        "username": username
    }
    
    headers = {
        "apikey": SCRAPEASAP_KEY,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:

        response = await client.post(url, json=payload, headers=headers, timeout=30.0)
    
    await DecreaseBlance(userkey, cost)

    return{"scraped data": response.json()}





