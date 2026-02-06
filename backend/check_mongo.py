import os
from pymongo import MongoClient

def check_mongo():
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    print(f"Testing connection to: {mongo_url}")
    
    try:
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=2000)
        # Force a connection check
        client.admin.command('ping')
        print("SUCCESS: Connected to MongoDB!")
        return True
    except Exception as e:
        print(f"FAILURE: Could not connect to MongoDB. Error: {e}")
        return False

if __name__ == "__main__":
    check_mongo()
