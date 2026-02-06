
# --- COMMUNITY FEATURES ---

from datetime import datetime

# Collections
feedback_collection = db["feedback"]
reviews_collection = db["reviews"]
chat_collection = db["chat_messages"]

@router.post("/community/feedback")
async def submit_feedback(feedback: Feedback):
    new_feedback = feedback.dict()
    new_feedback["timestamp"] = datetime.now().isoformat()
    feedback_collection.insert_one(new_feedback)
    return {"message": "Feedback submitted successfully"}

@router.get("/community/reviews")
async def get_reviews():
    reviews = []
    cursor = reviews_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(20)
    for review in cursor:
        reviews.append(review)
    return reviews or []

@router.post("/community/reviews")
async def submit_review(review: Review):
    new_review = review.dict()
    new_review["timestamp"] = datetime.now().isoformat()
    reviews_collection.insert_one(new_review)
    return {"message": "Review submitted successfully"}

@router.get("/community/chat")
async def get_chat_messages():
    messages = []
    cursor = chat_collection.find({}, {"_id": 0}).sort("timestamp", 1).limit(50) # Oldest first for chat history? Or newest? Usually chat is chronological.
    for msg in cursor:
        messages.append(msg)
    return messages or []

@router.post("/community/chat")
async def send_chat_message(message: ChatMessage):
    new_msg = message.dict()
    new_msg["timestamp"] = datetime.now().isoformat()
    chat_collection.insert_one(new_msg)
    return {"message": "Message sent"}
