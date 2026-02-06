from pymongo import MongoClient
import os

# Use local MongoDB - change to Atlas URL if needed
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)

db = client["auth_db"]
users_collection = db["users"]
reviews_collection = db["reviews"]
activity_collection = db["activity"]
feedback_collection = db["feedback"]
chat_collection = db["chat"]
schemes_collection = db["schemes"]
jobs_collection = db["jobs"]
applications_collection = db["applications"]
