from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

try:
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    db = client["auth_db"]
    users = list(db["users"].find({}, {"password": 0}))
    print(f"Total users found: {len(users)}")
    for user in users:
        print(f"User: {user.get('email')} | Name: {user.get('name')}")
except Exception as e:
    print(f"Error: {e}")
