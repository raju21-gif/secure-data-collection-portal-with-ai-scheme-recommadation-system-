from pymongo import MongoClient
import os

MONGO_URL = "mongodb+srv://badboy:raju21@cluster0.ff7qspu.mongodb.net/?appName=Cluster0"

try:
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
    print("Connection Successful!")
    db = client["auth_db"]
    user_count = db["users"].count_documents({})
    print(f"Users in database: {user_count}")
except Exception as e:
    print(f"Connection Failed: {e}")
