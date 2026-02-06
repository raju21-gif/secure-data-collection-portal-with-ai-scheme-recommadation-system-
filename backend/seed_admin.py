from pymongo import MongoClient
import os
from auth import get_password_hash
from dotenv import load_dotenv

# Load environment variables (MONGO_URL)
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = MongoClient(MONGO_URL)
db = client["auth_db"]
users_collection = db["users"]

def seed_admin():
    admin_email = "admin@freedy.ai"
    admin_password = "admin123" # You can change this
    
    # Check if admin already exists
    if users_collection.find_one({"email": admin_email}):
        print(f"Admin {admin_email} already exists.")
        return

    hashed_password = get_password_hash(admin_password)
    
    admin_user = {
        "name": "System Administrator",
        "email": admin_email,
        "password": hashed_password,
        "role": "admin",
        "image_url": "/uploads/admin.png"
    }
    
    users_collection.insert_one(admin_user)
    print(f"Successfully seeded admin: {admin_email} with role: admin")

if __name__ == "__main__":
    seed_admin()
