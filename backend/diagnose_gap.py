import pandas as pd
import os

# Define path (mimic recommendation_engine.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.path.join(DATA_DIR, "job.csv")

print(f"Checking Job CSV at: {CSV_PATH}")

if not os.path.exists(CSV_PATH):
    print("ERROR: File not found!")
    exit(1)

try:
    df = pd.read_csv(CSV_PATH)
    print("CSV Loaded Successfully.")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Total Rows: {len(df)}")
    
    # Normalize columns
    df.columns = [c.lower().strip() for c in df.columns]
    
    # Check Sample Data
    print("\n--- Sample Row 1 ---")
    print(df.iloc[0]['job_domains'])
    print(df.iloc[0]['skill_requirements'])
    
    # Test Matching Logic
    target_roles = ["full stack", "software engineer", "software deveeoper", "Software Engineer,AI/ML,Cloud"]
    
    print("\n--- Testing Matches ---")
    for role in target_roles:
        role_clean = role.lower().strip()
        print(f"\nTarget: '{role_clean}'")
        
        # Strict Match
        matches = df[
            df['job_domains'].fillna('').str.lower().str.contains(role_clean, regex=False) |
            df['name'].fillna('').str.lower().str.contains(role_clean, regex=False)
        ]
        print(f"Strict Matches: {len(matches)}")
        
        # Partial Match
        if matches.empty and len(role_clean.split()) > 1:
            keywords = [k for k in role_clean.split() if len(k) > 2]
            print(f"Trying keywords: {keywords}")
            mask = pd.Series([False] * len(df))
            for kw in keywords:
                 mask |= df['job_domains'].fillna('').str.lower().str.contains(kw, regex=False)
                 mask |= df['name'].fillna('').str.lower().str.contains(kw, regex=False)
            matches = df[mask]
            print(f"Partial Matches: {len(matches)}")

        if not matches.empty:
            # Check skills extraction
            required_skills = set()
            for s_str in matches['skill_requirements'].fillna(''):
                skills = [s.strip() for s in s_str.split(',') if s.strip()]
                required_skills.update(skills)
            print(f"Found {len(required_skills)} skills: {list(required_skills)[:5]}...")
        else:
            print("NO MATCHES FOUND")

except Exception as e:
    print(f"ERROR: {e}")
