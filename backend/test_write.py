from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

try:
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    db = client["auth_db"]
    test_user = {"email": "test@test.com", "name": "Test User"}
    db["users"].delete_many({"email": "test@test.com"}) # Clean up
    result = db["users"].insert_one(test_user)
    print(f"Write successful! Created ID: {result.inserted_id}")
    
    users = list(db["users"].find({}, {"password": 0}))
    print(f"Total users now: {len(users)}")
    for user in users:
        print(f" - {user.get('email')}")
except Exception as e:
    print(f"Write failed: {e}")
