# ======================================================
# main.py
# Hybrid AI Scheme Recommendation System (FIXED)
# Transformer + Backpropagation + HARD CATEGORY FILTER
# ======================================================

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ======================================================
# FASTAPI APP INIT
# ======================================================

app = FastAPI(
    title="AI Scheme Recommendation API",
    description="Hybrid AI using Transformer + Backpropagation with strict category filtering",
    version="3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# LOAD CSV DATASET (SAFE)
# ======================================================

df = pd.read_csv("schemes.csv", engine="python")
df.columns = df.columns.str.strip().str.lower()

# Ensure required columns exist
required_columns = [
    "scheme_name",
    "description",
    "eligibility",
    "benefits",
    "official_link"
]

for col in required_columns:
    if col not in df.columns:
        df[col] = ""

# ======================================================
# RULE-BASED CATEGORY DETECTION
# ======================================================

def detect_category(text: str) -> str:
    text = str(text).lower()
    if "kisan" in text or "farmer" in text or "crop" in text or "agriculture" in text:
        return "farmer"
    elif "student" in text or "education" in text or "scholar" in text or "vidya" in text:
        return "student"
    elif "pension" in text or "senior" in text or "old age" in text:
        return "senior"
    elif "health" in text or "insurance" in text or "medical" in text:
        return "health"
    else:
        return "general"

# Use both name and description for better context
df["text_context"] = df["scheme_name"].astype(str) + " " + df["description"].astype(str)
df["category"] = df["text_context"].apply(detect_category)

# ======================================================
# TRANSFORMER ENCODER (OFFLINE SAFE)
# ======================================================

model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    device="cpu"
)

df["text"] = (
    df["scheme_name"].astype(str) + ". " +
    df["description"].astype(str) + ". " +
    df["benefits"].astype(str)
)

scheme_embeddings = model.encode(df["text"].tolist())

# ======================================================
# BACKPROPAGATION (SIMULATED NEURAL NETWORK)
# ======================================================

WEIGHTS = {
    "age": 0.2,
    "income": 0.3,
    "occupation": 0.3,
    "health": 0.2
}

OCCUPATION_MAP = {
    "farmer": 1,
    "student": 1,
    "senior": 1,
    "health": 1,
    "general": 0
}

def neural_network_score(age, income, occupation, health):
    age_norm = min(age / 100, 1)
    income_norm = min(income / 500000, 1)
    occupation_enc = OCCUPATION_MAP.get(occupation, 0)
    health_enc = 1 if health == "yes" else 0

    inputs = np.array([
        age_norm,
        income_norm,
        occupation_enc,
        health_enc
    ])

    weighted_sum = np.dot(
        inputs,
        np.array([
            WEIGHTS["age"],
            WEIGHTS["income"],
            WEIGHTS["occupation"],
            WEIGHTS["health"]
        ])
    )

    return float(1 / (1 + np.exp(-weighted_sum)))

# ======================================================
# USER INPUT SCHEMA
# ======================================================

class UserInput(BaseModel):
    first_name: str
    age: int
    occupation: str
    income: int
    health: str
    need: str

# ======================================================
# ROOT ENDPOINT
# ======================================================

@app.get("/")
def root():
    return {"status": "AI Scheme Recommendation API running (FIXED)"}

# ======================================================
# MAIN RECOMMENDATION API (FIXED LOGIC)
# ======================================================

@app.post("/recommend")
def recommend(user: UserInput):

    occupation = user.occupation.lower()
    health = user.health.lower()

    # -------------------------------
    # 1. HARD CATEGORY FILTER  ✅ FIX
    # -------------------------------
    if occupation in ["farmer", "student", "senior", "health"]:
        data = df[df["category"].isin([occupation, "general"])].copy()
    else:
        data = df.copy()

    # -------------------------------
    # 2. BACKPROPAGATION SCORE
    # -------------------------------
    bp_score = neural_network_score(
        user.age,
        user.income,
        occupation,
        health
    )

    # -------------------------------
    # 3. TRANSFORMER USER EMBEDDING
    # -------------------------------
    user_text = (
        f"{user.age} years old {occupation} "
        f"with income {user.income}. "
        f"Need: {user.need}"
    )

    user_embedding = model.encode([user_text])
    transformer_scores = cosine_similarity(
        user_embedding,
        scheme_embeddings[data.index]
    )[0]

    # -------------------------------
    # 4. FINAL HYBRID SCORE
    # -------------------------------
    data["transformer_score"] = transformer_scores
    data["bp_score"] = bp_score

    data["final_score"] = (
        0.6 * data["transformer_score"] +
        0.4 * data["bp_score"]
    )

    # -------------------------------
    # 5. TOP RESULTS WITH SHUFFLE (To show different 6 on refresh)
    # -------------------------------
    # Get top 20 candidates first
    candidates = data.sort_values(
        by="final_score",
        ascending=False
    ).head(20).copy()

    # Shuffle the top candidates
    shuffled = candidates.sample(frac=1).reset_index(drop=True)
    
    # Take top 6
    top6 = shuffled.head(6)

    return {
        "user": user.first_name,
        "occupation": occupation,
        "model": "Hybrid AI (Transformer + Backpropagation)",
        "recommendations": top6[[
            "scheme_name",
            "description",
            "benefits",
            "official_link"
        ]].to_dict(orient="records")
    }
