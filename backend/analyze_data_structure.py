import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.path.join(DATA_DIR, "job.csv")

def analyze_structure():
    print(f"--- ANALYZING STRUCTURE OF: {CSV_PATH} ---\n")
    
    if not os.path.exists(CSV_PATH):
        print("CRITICAL: job.csv not found.")
        return

    try:
        df = pd.read_csv(CSV_PATH)
        df.columns = [c.lower().strip() for c in df.columns]
        
        # 1. Basic Stats
        print(f"Total Rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        print("-" * 30)

        # 2. Validity Checks
        missing_domains = df[df['job_domains'].isna()]
        missing_skills = df[df['skill_requirements'].isna()]
        
        if not missing_domains.empty:
            print(f"WARNING: {len(missing_domains)} rows have MISSING 'job_domains'. IDs: {missing_domains['id'].tolist()}")
        else:
            print("OK: All rows have 'job_domains'.")

        if not missing_skills.empty:
            print(f"WARNING: {len(missing_skills)} rows have MISSING 'skill_requirements'. IDs: {missing_skills['id'].tolist()}")
        else:
            print("OK: All rows have 'skill_requirements'.")

        # 3. Domain Analysis (Roles)
        all_domains = set()
        for domains in df['job_domains'].dropna():
            # Split by comma
            parts = [d.strip() for d in domains.split(',')]
            all_domains.update(parts)
        
        print(f"\nUnique Job Roles Found: {len(all_domains)}")
        print(f"Sample Roles: {list(all_domains)[:10]}...")

        # 4. Skill Analysis
        all_skills = set()
        for skills in df['skill_requirements'].dropna():
            parts = [s.strip() for s in skills.split(',')]
            all_skills.update(parts)
            
        print(f"Unique Skills Database: {len(all_skills)}")
        print(f"Sample Skills: {list(all_skills)[:10]}...")
        
        # 5. Structure Validation
        # Check if ID is unique
        if df['id'].is_unique:
             print("\nOK: 'id' column is unique.")
        else:
             print("\nWARNING: 'id' column has duplicates!")

        print("\n--- CONCLUSION ---")
        if len(missing_domains) == 0 and len(missing_skills) == 0:
            print("The data structure appears SOLID for basic recommendation logic.")
        else:
            print("The data requires CLEANING.")

    except Exception as e:
        print(f"ERROR reading CSV: {e}")

if __name__ == "__main__":
    analyze_structure()
