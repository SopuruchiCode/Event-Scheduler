from pymongo import AsyncMongoClient
from dotenv import load_dotenv
from os import getenv



load_dotenv()

db_username = getenv("MONGO_DB_USERNAME")
db_password = getenv("MONGO_DB_PASSWORD")
MEDIA_FOLDER = "MEDIA"
connection_string = f"mongodb://{db_username}:{db_password}@localhost:27017/"
client = AsyncMongoClient(connection_string)

USER_DATABASE = client["auth"]["users"]
REFRESH_TOKEN_DATABASE = client["auth"]["refresh-tokens"]

async def get_user(username):
    db = client["auth"]["users"]
    user = await db.find_one(filter={"username":username})
    
    return user
