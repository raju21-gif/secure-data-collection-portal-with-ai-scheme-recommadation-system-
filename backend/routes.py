from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from database import users_collection, reviews_collection, activity_collection, feedback_collection, chat_collection, schemes_collection, jobs_collection, applications_collection
from models import Token, UserResponse, Feedback, Review, ChatMessage
from datetime import timedelta, datetime
from typing import Annotated, Optional
from pydantic import BaseModel
import shutil
import shutil
import os
from recommendation_engine import RecommendationEngine

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/health")
async def health_check():
    from database import MONGO_URL
    # Mask password for security
    masked_url = MONGO_URL.split("@")[-1] if "@" in MONGO_URL else "Local/Other"
    try:
        users_collection.count_documents({})
        status = "Connected"
    except Exception as e:
        status = f"Failed: {str(e)}"
    
    return {
        "status": status,
        "database_host": masked_url,
        "collection": users_collection.name
    }

@router.post("/register")
async def register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    image: UploadFile = File(...)
):
    email = email.lower().strip()
    if users_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Save Image safely
    safe_filename = "".join([c for c in image.filename if c.isalnum() or c in "._-"]).strip()
    if not safe_filename:
        safe_filename = f"user_{email.split('@')[0]}.png"
        
    image_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    try:
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    except Exception as e:
        print(f"Error saving image: {e}")
        # If image save fails, we can still proceed with placeholder or return error
        # but for now let's try to proceed to avoid total failure
        safe_filename = "default.png"
    
    hashed_password = get_password_hash(password)
    try:
        new_user = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "image_url": f"/uploads/{safe_filename}"
        }
        users_collection.insert_one(new_user)
        print(f"Successfully registered user: {email}")
    except Exception as e:
        print(f"DATABASE ERROR during registration: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Return user info without password
    return {"message": "User registered successfully", "user": {"name": name, "email": email}}

@router.post("/login")
async def login(
    username: str = Form(...), # Frontend might send 'username' key for email
    password: str = Form(...)
):
    username = username.lower().strip()
    # Case-insensitive search (still using regex just in case database has unnormalized data)
    user = users_collection.find_one({"email": {"$regex": f"^{username}$", "$options": "i"}})
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.get("role", "user"),
        "user": {
            "name": user["name"],
            "email": user["email"],
            "image_url": user.get("image_url", ""),
            "role": user.get("role", "user")
        }
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    # Map _id to string if needed, or just return dict
    return {
        "name": current_user["name"],
        "email": current_user["email"],
        "role": current_user.get("role", "user"),
        "image_url": current_user.get("image_url", "")
    }

async def get_current_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )
    return current_user

@router.get("/admin/users")
async def get_all_users(admin_user: dict = Depends(get_current_admin)):
    users = []
    for user in users_collection.find({}, {"_id": 0, "password": 0}):
        users.append(user)
    return users

@router.delete("/admin/users/{email}")
async def delete_user(email: str, admin_user: dict = Depends(get_current_admin)):
    result = users_collection.delete_one({"email": email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User {email} deleted successfully"}

@router.get("/admin/stats")
async def get_stats(admin_user: dict = Depends(get_current_admin)):
    total_users = users_collection.count_documents({})
    import random
    from datetime import datetime
    
    # Fluctuation: Base active users is around 60% of total
    base_active = int(total_users * 0.6) if total_users > 0 else 0
    # Add random jitter +/- 5%
    jitter = int(total_users * 0.05) if total_users > 0 else 1
    active_now = max(0, min(total_users, base_active + random.randint(-jitter, jitter)))
    
    # Simulate System Load (0-100%)
    system_load = random.randint(10, 45)
    
    return {
        "total_users": total_users,
        "active_now": active_now,
        "system_load": system_load,
        "schemes_count": 84, # Placeholder or fetch real
        "timestamp": datetime.now().isoformat()
    }

# --- ACTIVITY LOGGING ---

from database import db # Ensure db is imported or accessible to create new collection
activity_collection = db["activity_logs"]

class ActivityLog(BaseModel):
    user_email: str
    action: str # e.g., "VIEWED_SCHEME", "APPLIED_SCHEME"
    target: str # e.g., "Maternity Benefit Scheme"
    timestamp: str = ""

@router.post("/activity/log")
async def log_activity(log: ActivityLog):
    new_log = log.dict()
    new_log["timestamp"] = datetime.now().isoformat()
    activity_collection.insert_one(new_log)
    return {"status": "logged"}

@router.post("/community/feedback")
async def submit_feedback(feedback: Feedback):
    new_feedback = feedback.dict()
    new_feedback["timestamp"] = datetime.now().isoformat()
    feedback_collection.insert_one(new_feedback)
    return {"message": "Feedback submitted successfully"}

@router.get("/community/feedback")
async def get_feedback():
    feedback_list = []
    cursor = feedback_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(50)
    for f in cursor:
        feedback_list.append(f)
    return feedback_list

@router.post("/community/reviews")
async def submit_review(review: Review):
    new_review = review.dict()
    new_review["timestamp"] = datetime.now().isoformat()
    reviews_collection.insert_one(new_review)
    
    # Log to Activity Stream
    try:
        activity_collection.insert_one({
            "user_email": "system", # Or specific user email if we had it in the model, using system/name for now
            "action": "POSTED_REVIEW",
            "target": f"Rated {review.rating} stars",
            "timestamp": datetime.now().isoformat()
        })
    except:
        pass
        
    return {"message": "Review submitted successfully"}

@router.get("/community/reviews")
async def get_reviews():
    reviews_list = []
    # Get recent reviews, sort by timestamp desc
    cursor = reviews_collection.find({}).sort("timestamp", -1).limit(50)
    for review in cursor:
        review["_id"] = str(review["_id"])
        reviews_list.append(review)
    return reviews_list

@router.delete("/community/reviews/{review_id}")
async def delete_review(review_id: str, current_user: dict = Depends(get_current_user)):
    from bson import ObjectId
    try:
        # Find review first to check ownership
        review = reviews_collection.find_one({"_id": ObjectId(review_id)})
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        # Check if user is owner or admin
        if review.get("user_email") != current_user["email"] and current_user["role"] != "admin":
             raise HTTPException(status_code=403, detail="Not authorized to delete this review")
        
        # Delete review
        reviews_collection.delete_one({"_id": ObjectId(review_id)})
        return {"message": "Review deleted successfully"}
    except Exception as e:
        print(f"Error deleting review: {e}")
        raise HTTPException(status_code=400, detail="Invalid review ID")

@router.post("/community/chat")
async def post_chat_message(message: ChatMessage):
    new_message = message.dict()
    new_message["timestamp"] = datetime.now().isoformat()
    chat_collection.insert_one(new_message)
    return {"status": "sent"}

@router.get("/community/chat")
async def get_chat_messages():
    messages = []
    # Get recent 50 messages, sorted by timestamp asc (oldest first)
    cursor = chat_collection.find({}, {"_id": 0}).sort("timestamp", 1).limit(50)
    for msg in cursor:
        messages.append(msg)
    return messages

@router.get("/admin/activity")
async def get_admin_activity(admin_user: dict = Depends(get_current_admin)):
    # Get last 20 logs, newest first
    logs = []
    # Sort by _id desc (natural time order) or timestamp if indexed
    cursor = activity_collection.find({}, {"_id": 0}).sort("_id", -1).limit(20)
    for log in cursor:
        logs.append(log)
    return logs

# --- RECOMMENDATION ENGINE ---

recommendation_engine = RecommendationEngine()

class RecommendationRequest(BaseModel):
    occupation: str = ""
    skills: str = ""
    qualification: str = ""
    interest: str = ""
    location: str = ""

@router.get("/admin/analytics/schemes")
async def get_scheme_analytics(admin_user: dict = Depends(get_current_admin)):
    pipeline = [
        {"$match": {"action": {"$in": ["VIEWED_DETAILS", "APPLIED_SCHEME"]}}},
        {"$group": {"_id": "$target", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    results = list(activity_collection.aggregate(pipeline))
    
    # Simulation logic for demonstration if no real activity exists
    if not results:
        import random
        # Pick some famous schemes for simulation
        schemes = ["Pradhan Mantri Jan Dhan Yojana", "Ayushman Bharat Yojana", "PM Kisan Samman Nidhi", "PM Awas Yojana Rural", "MGNREGA"]
        return [{"name": s, "value": random.randint(5, 50)} for s in schemes]

    # Map to frontend friendly format
    return [{"name": r["_id"], "value": r["count"]} for r in results]

@router.get("/admin/analytics/jobs")
async def get_job_analytics(admin_user: dict = Depends(get_current_admin)):
    pipeline = [
        {"$match": {"action": "VISITED_JOB_PORTAL"}},
        {"$group": {"_id": "$target", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    results = list(activity_collection.aggregate(pipeline))

    # Simulation logic for demonstration if no real activity exists
    if not results:
        import random
        portals = ["Naukri.com", "Indeed India", "LinkedIn Jobs", "Monster India", "Internshala"]
        return [{"name": p, "value": random.randint(5, 50)} for p in portals]

    return [{"name": r["_id"], "value": r["count"]} for r in results]

@router.get("/admin/inventory/jobs")
async def get_job_inventory(admin_user: dict = Depends(get_current_admin)):
    import pandas as pd
    CSV_PATH = os.path.join(os.path.dirname(__file__), 'data/job.csv')
    try:
        df = pd.read_csv(CSV_PATH)
        df = df.fillna("")
        return df.to_dict(orient='records')
    except Exception as e:
        print(f"Error reading jobs CSV: {e}")
        raise HTTPException(status_code=500, detail="Failed to load job inventory")

@router.get("/admin/analytics/usage")
async def get_usage_analytics(admin_user: dict = Depends(get_current_admin)):
    import random
    from datetime import datetime, timedelta
    
    # Generate last 7 days of simulated usage data
    usage_data = []
    base_users = 100
    for i in range(7, 0, -1):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        usage_data.append({
            "name": date,
            "usage": base_users + random.randint(20, 200),
            "rating": round(random.uniform(4.0, 5.0), 1)
        })
    return usage_data

@router.get("/admin/inventory/schemes")
async def get_scheme_inventory(admin_user: dict = Depends(get_current_admin)):
    import pandas as pd
    CSV_PATH = os.path.join(os.path.dirname(__file__), '../scheme/schemes.csv')
    try:
        df = pd.read_csv(CSV_PATH)
        # Fill NaN values with empty string for JSON compatibility
        df = df.fillna("")
        return df.to_dict(orient='records')
    except Exception as e:
        print(f"Error reading schemes CSV: {e}")
        raise HTTPException(status_code=500, detail="Failed to load scheme inventory")

@router.post("/recommend")
async def get_recommendations(request: RecommendationRequest):
    return recommendation_engine.get_recommendations(request.dict())

class SkillGapRequest(BaseModel):
    user_skills: list[str]
    target_role: str

@router.post("/analyze-skill-gap")
async def analyze_skill_gap(request: SkillGapRequest):
    return recommendation_engine.analyze_skill_gap(request.user_skills, request.target_role)


# --- MOCK INTERVIEW BOT ---

from interview_bot import InterviewBot
interview_bot = InterviewBot()

# Initialize MongoDB Collection
interview_collection = db["interview_sessions"]


class InterviewStartRequest(BaseModel):
    role: str
    mode: str = "full" # or 'intro'
    resume_text: str = ""
    difficulty: int = 5 # Default start difficulty

class InterviewSubmitRequest(BaseModel):
    role: str
    question: str
    answer: str
    code: Optional[str] = None
    mode: str = "full"
    language: str = "English"
    current_difficulty: int = 5 # Pass current level
    # In real app, we should pass a session_id to group Q&A

@router.post("/interview/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    try:
        # Save temp file
        temp_path = f"uploads/temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        extracted_text = ""
        
        # Parse PDF
        if file.filename.lower().endswith('.pdf'):
            try:
                from pypdf import PdfReader
                reader = PdfReader(temp_path)
                for page in reader.pages:
                    extracted_text += page.extract_text() + "\n"
            except ImportError:
                return {"error": "pypdf not installed on server."}
            except Exception as e:
                return {"error": f"Failed to parse PDF: {str(e)}"}
                
        # Parse Text
        elif file.filename.lower().endswith('.txt'):
            with open(temp_path, "r", encoding="utf-8") as f:
                extracted_text = f.read()
        
        else:
            return {"error": "Unsupported file format. Please upload PDF or TXT."}
            
        # Cleanup
        os.remove(temp_path)
        
        # Limit text size for context window
        return {"resume_text": extracted_text[:5000]} # Return first 5000 chars
        
    except Exception as e:
        return {"error": f"Upload failed: {str(e)}"}

@router.post("/interview/start")
async def start_interview(request: InterviewStartRequest):
    # Pass resume_text    # Generate initial question
    result = interview_bot.generate_question(
        role=request.role,
        mode=request.mode,
        difficulty=request.difficulty
    )
    return result

@router.post("/interview/submit")
async def submit_answer(request: InterviewSubmitRequest):
    # 1. Evaluate current answer
    evaluation = interview_bot.evaluate_answer(
        request.role, 
        request.question, 
        request.answer, 
        code_input=request.code,
        mode=request.mode,
        language=request.language,
        current_difficulty=request.current_difficulty
    )
    
    # Get the recommended next difficulty from evaluation
    next_difficulty = evaluation.get("next_difficulty", request.current_difficulty)
    
    # 2. Get next question (mock history for now, or just send current Q/A)
    # In a real app, we'd persist history in DB. Here we just pass last Q/A context implicitly if needed.
    history = [{"question": request.question, "answer": request.answer}]
    
    # Generate next question with NEW difficulty
    next_q_data = interview_bot.generate_question(
        request.role, 
        history, 
        mode=request.mode, 
        difficulty=next_difficulty
    )
    
    return {
        "evaluation": evaluation,
        "next_question": next_q_data
    }



