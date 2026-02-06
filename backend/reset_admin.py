from pymongo import MongoClient
import os
from auth import get_password_hash
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = MongoClient(MONGO_URL)
db = client["auth_db"]
users_collection = db["users"]

def reset_password():
    email = "admin@freedy.ai"
    password = "admin123"
    hashed = get_password_hash(password)
    
    result = users_collection.update_one(
        {"email": {"$regex": f"^{email}$", "$options": "i"}},
        {"$set": {"password": hashed, "role": "admin"}},
        upsert=True
    )
    if result.matched_count > 0:
        print(f"Updated password for {email}")
    else:
        print(f"Created new admin {email}")

if __name__ == "__main__":
    reset_password()
