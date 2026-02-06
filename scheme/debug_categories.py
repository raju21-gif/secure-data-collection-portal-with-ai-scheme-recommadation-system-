import pandas as pd
import numpy as np

# Load data
try:
    df = pd.read_csv("schemes.csv", engine="python")
    df.columns = df.columns.str.strip().str.lower()
    print("Loaded schemes.csv successfully.")
except Exception as e:
    print(f"Error loading CSV: {e}")
    exit()

def detect_category(text: str) -> str:
    text = str(text).lower()
    if "kisan" in text or "farmer" in text or "crop" in text:
        return "farmer"
    elif "student" in text or "education" in text or "scholar":
        return "student"
    elif "pension" in text or "senior":
        return "senior"
    elif "health" in text or "insurance":
        return "health"
    else:
        return "general"

# Apply detection
print("\n--- Categorization Logic Check ---")
df["category_name_only"] = df["scheme_name"].apply(detect_category)

# Improved detection (checking description too - proposed fix)
df["text_for_detection"] = df["scheme_name"].astype(str) + " " + df["description"].astype(str)
df["category_improved"] = df["text_for_detection"].apply(detect_category)

print("Categories (Name Only):")
print(df["category_name_only"].value_counts())
print("\nCategories (Name + Desc):")
print(df["category_improved"].value_counts())

print("\n--- 'Farmer' Category Schemes (Name Only) ---")
print(df[df["category_name_only"] == "farmer"]["scheme_name"].tolist())

print("\n--- 'Farmer' Category Schemes (Improved) ---")
print(df[df["category_improved"] == "farmer"]["scheme_name"].tolist())

# Simulate Request logic
occupation = "farmer"
# Current Logic in main.py (Name Only)
df["category"] = df["category_name_only"]

if occupation in ["farmer", "student", "senior", "health"]:
    data = df[df["category"].isin([occupation, "general"])].copy()
else:
    data = df.copy()

print(f"\n--- Simulation for '{occupation}' ---")
print(f"Total schemes after filtering (Farmer + General): {len(data)}")
print("First 10 filtered schemes:")
print(data["scheme_name"].head(10).tolist())
