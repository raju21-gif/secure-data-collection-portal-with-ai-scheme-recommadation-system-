from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.staticfiles import StaticFiles
from routes import router

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
import requests

# Import our new modules
from ai_engine import get_ai_response
from whatsapp_twilio import handle_twilio_message

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

app = FastAPI()

# Mount uploads directory to serve images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(router)


# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Schemes Data
CSV_PATH = os.path.join(os.path.dirname(__file__), '../scheme/schemes.csv')

def load_schemes():
    try:
        return pd.read_csv(CSV_PATH)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

# Request Models
class UserData(BaseModel):
    fullName: str = ""
    age: str = ""
    occupation: str = ""
    income: str = ""
    fatherName: str = ""
    motherName: str = ""

class ChatRequest(BaseModel):
    message: str
    context: str = ""

# ... (rest of scheme logic) ...

def get_relevant_schemes(df, user_data):
    """
    AI-based scheme recommendation logic.
    Filters and ranks schemes based on user profile.
    """
    schemes_list = df.to_dict(orient='records')
    scored_schemes = []
    
    # Parse user data
    age = 0
    try:
        age = int(user_data.age) if user_data.age else 0
    except:
        pass
    
    occupation = user_data.occupation.lower() if user_data.occupation else ""
    income = user_data.income.lower() if user_data.income else ""
    
    # Keywords for different categories
    farmer_keywords = ['farmer', 'agriculture', 'farming', 'kisan', 'fasal', 'crop']
    student_keywords = ['student', 'education', 'scholarship', 'school', 'learning', 'study']
    senior_keywords = ['senior', 'old age', 'pension', 'elder', 'retirement']
    women_keywords = ['women', 'woman', 'girl', 'beti', 'widow', 'mahila']
    health_keywords = ['health', 'medical', 'hospital', 'insurance', 'arogya']
    skill_keywords = ['skill', 'training', 'employment', 'job', 'career']
    business_keywords = ['business', 'startup', 'entrepreneur', 'loan', 'mudra', 'vendor']
    low_income_keywords = ['poor', 'bpl', 'rural', 'housing', 'awas', 'ration']
    
    for scheme in schemes_list:
        score = 0
        name = scheme.get('scheme_name', '').lower()
        desc = scheme.get('description', '').lower()
        scheme_text = name + " " + desc
        
        # Age-based scoring
        if age > 0:
            if age < 25 and any(kw in scheme_text for kw in student_keywords):
                score += 3
            if age >= 60 and any(kw in scheme_text for kw in senior_keywords):
                score += 3
            if age >= 18 and age <= 35 and any(kw in scheme_text for kw in skill_keywords):
                score += 2
        
        # Occupation-based scoring
        if 'farmer' in occupation or 'agriculture' in occupation:
            if any(kw in scheme_text for kw in farmer_keywords):
                score += 3
        if 'student' in occupation:
            if any(kw in scheme_text for kw in student_keywords):
                score += 3
        if 'business' in occupation or 'entrepreneur' in occupation:
            if any(kw in scheme_text for kw in business_keywords):
                score += 3
        
        # Income-based scoring
        if 'low' in income or 'poor' in income or any(x in income for x in ['0', '1', '2', '3', '4', '5']):
            if any(kw in scheme_text for kw in low_income_keywords):
                score += 2
        
        # General relevance - always include some health and skill schemes
        if any(kw in scheme_text for kw in health_keywords):
            score += 1
        if any(kw in scheme_text for kw in skill_keywords):
            score += 1
            
        scored_schemes.append((score, scheme))
    
    # Sort by score (highest first) and take top 6
    scored_schemes.sort(key=lambda x: x[0], reverse=True)
    top_schemes = [s[1] for s in scored_schemes[:6]]
    
    # If no high-scoring schemes, return random mix
    if all(s[0] == 0 for s in scored_schemes[:6]):
        return df.sample(n=min(6, len(df))).to_dict(orient='records')
    
    return top_schemes

# @app.post("/recommend")
# async def recommend(user_data: UserData):
#     print("Received user data:", user_data.model_dump())
    
#     df = load_schemes()
#     if df is None:
#         return {"error": "Schemes data not found"}

#     # Get relevant schemes based on user profile
#     recommended_schemes = get_relevant_schemes(df, user_data)
    
#     return {"schemes": recommended_schemes}

@app.post("/chat")
async def chat(request: ChatRequest):
    # Use the shared AI engine
    reply = get_ai_response(request.message, request.context)
    return {"reply": reply}

@app.post("/whatsapp")
async def whatsapp_endpoint(request: Request):
    return await handle_twilio_message(request)

@app.get("/")
async def root():
    return {"message": "Scheme Recommendation API is running"}

