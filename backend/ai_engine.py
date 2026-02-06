import os
import requests
import json
from dotenv import load_dotenv
from recommendation_engine import RecommendationEngine

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Initialize the engine once
rec_engine = RecommendationEngine()

def get_ai_response(message: str, context: str = "") -> str:
    """
    AI logic using OpenRouter (DeepSeek R1) + Local Recommendation Engine.
    """
    msg_lower = message.lower().strip()

    # 1. Get Local Recommendations for Context
    # Simple keyword extraction
    stopwords = ["i", "need", "want", "for", "a", "the", "please", "give", "me", "am", "looking", "scheme", "loan", "help", "how", "what", "is"]
    keywords = [w for w in msg_lower.split() if w not in stopwords]
    
    user_profile = {
        "occupation": "citizen", # Default
        "skills": ",".join(keywords),
        "interest": ",".join(keywords),
        "location": "india"
    }
    
    # Detect occupation for better local matching
    if any(k in msg_lower for k in ["farmer", "agriculture", "kisan"]):
        user_profile["occupation"] = "farmer"
    elif any(k in msg_lower for k in ["student", "study", "education", "degree"]):
        user_profile["occupation"] = "student"
    elif any(k in msg_lower for k in ["business", "startup", "entrepreneur", "shop"]):
        user_profile["occupation"] = "business"

    # Get local data
    local_results = rec_engine.get_recommendations(user_profile)
    schemes = local_results.get("schemes", [])[:3] # Top 3
    
    # Format context for AI
    schemes_context = ""
    if schemes:
        schemes_context = "Here are some relevant schemes from our database:\n"
        for i, s in enumerate(schemes, 1):
            schemes_context += f"{i}. Name: {s.get('scheme_name')}, Type: {s.get('scheme_type')}, Link: {s.get('official_link')}, Desc: {s.get('description')}\n"

    # 2. Call OpenRouter API
    if not OPENROUTER_API_KEY:
        return "Error: API Key not found. Please check your .env file."

    system_prompt = f"""You are 'Keran AI', a helpful and friendly government scheme assistant. 
    Your goal is to help users find relevant government and private schemes.
    
    {schemes_context}
    
    Guidelines:
    - If relevant schemes are provided in the context above, highlight them clearly.
    - Be polite, professional, and use emojis to make the conversation engaging.
    - Keep responses concise but informative.
    - If you don't find a specific scheme, suggest general categories or how to apply.
    - Use the existing links provided in the context for specific schemes.
    - Respond in the language requested by the user context if possible.
    """

    api_url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek/deepseek-r1",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User Context: {context}\nUser Message: {message}"}
        ]
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        ai_reply = data['choices'][0]['message']['content']
        
        # Clean up <think> tags if present (common in DeepSeek R1)
        import re
        ai_reply = re.sub(r'<think>[\s\S]*?</think>', '', ai_reply).strip()
        
        return ai_reply
    except Exception as e:
        print(f"AI API Error: {e}")
        # Fallback to local-only logic if API fails
        if not schemes:
            return "I'm having trouble connecting to my brain right now! Please try again later or search for keywords like 'farmer', 'student', or 'loan'."
        
        fallback_msg = "I'm currently having some connection issues, but based on our database, here are some schemes you might be interested in:\n\n"
        for i, s in enumerate(schemes, 1):
            fallback_msg += f"*{i}. {s.get('scheme_name')}*\n🔗 {s.get('official_link')}\n\n"
        return fallback_msg
