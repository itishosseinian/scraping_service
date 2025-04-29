from motor.motor_asyncio import AsyncIOMotorClient

from dotenv import load_dotenv
import os

load_dotenv()

MONGO_KEY = os.getenv("MONGO_KEY")

client = AsyncIOMotorClient(MONGO_KEY)
db = client.get_database("scraping_service")
user_collection = db.get_collection("users")


async def RegisterToDB(user_data):
    await user_collection.insert_one(user_data)

async def FindUserByEmail(email):
    user = await user_collection.find_one({"email": email})
    return user

async def FindUserByAPIKey(apikey):
    user = await user_collection.find_one({"apikey": apikey})
    return user

async def UpdateUserByEmail(email, plan_name, credits, expiry):
    await user_collection.update_one(
        {"email": email},
        {
            "$set": {
                "plan": plan_name,
                "credits": credits,
                "expiry": expiry
            }
        }
    )

async def DecreaseBlance(apikey, cost):
    await user_collection.update_one(
        {"apikey": apikey},
        {
            "$inc": {
                "credits": -cost
            }
        }
    )


