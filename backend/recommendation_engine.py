import pandas as pd
import os

class RecommendationEngine:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.data_path = os.path.join(self.base_path, "data")
        self.schemes_df = None
        self.jobs_df = None
        self.load_data()

    def load_data(self):
        try:
            schemes_path = os.path.join(self.data_path, "schemes.csv")
            jobs_path = os.path.join(self.data_path, "job.csv")
            
            if os.path.exists(schemes_path):
                self.schemes_df = pd.read_csv(schemes_path)
                # Normalize columns
                self.schemes_df.columns = [c.lower().strip() for c in self.schemes_df.columns]
                # Ensure description exists
                if 'description' not in self.schemes_df.columns:
                    self.schemes_df['description'] = ""
                self.schemes_df['combined_text'] = (
                    self.schemes_df['scheme_name'].fillna('') + " " + 
                    self.schemes_df['description'].fillna('') + " " + 
                    self.schemes_df['scheme_type'].fillna('')
                ).str.lower()
            
            if os.path.exists(jobs_path):
                self.jobs_df = pd.read_csv(jobs_path)
                self.jobs_df.columns = [c.lower().strip() for c in self.jobs_df.columns]
                if 'description' not in self.jobs_df.columns:
                    self.jobs_df['description'] = ""
                self.jobs_df['combined_text'] = (
                    self.jobs_df['name'].fillna('') + " " + 
                    self.jobs_df['description'].fillna('') + " " + 
                    self.jobs_df['type'].fillna('')
                ).str.lower()
                
        except Exception as e:
            print(f"Error loading data: {e}")

    def get_recommendations(self, user_profile: dict):
        """
        user_profile: {
            "occupation": str,
            "skills": str, # comma separated
            "interest": str, # comma separated
            "location": str
        }
        """
        if self.schemes_df is None or self.jobs_df is None:
            return {"schemes": [], "jobs": []}

        occupation = user_profile.get("occupation", "").lower()
        skills = [s.strip().lower() for s in user_profile.get("skills", "").split(",") if s.strip()]
        interests = [i.strip().lower() for i in user_profile.get("interest", "").split(",") if i.strip()]
        
        # --- Scheme Matching ---
        # Keywords for occupation
        occ_keywords = []
        if "student" in occupation or "graduating" in occupation:
            occ_keywords = ["scholarship", "education", "student", "learning", "skill", "training"]
        elif "unemployed" in occupation:
            occ_keywords = ["employment", "loan", "skill", "pension", "livelihood", "guarantee"]
        elif "employed" in occupation:
            occ_keywords = ["housing", "insurance", "pension", "tech", "finance"]
        elif "farmer" in occupation or "agriculture" in occupation:
            occ_keywords = ["farmer", "agriculture", "kisan", "crop", "loan", "irrigation", "rural"]
        elif "business" in occupation:
            occ_keywords = ["business", "loan", "msme", "startup", "credit", "entrepreneur"]
        elif "retired" in occupation:
             occ_keywords = ["pension", "senior", "health", "security"]
        else:
             # Default generic keywords if occupation is unknown/other
             occ_keywords = ["citizen", "welfare", "scheme", "financial", "support"]

        # Calculate Score
        def calculate_score(text, keywords):
            score = 0
            for kw in keywords:
                if kw in text:
                    score += 1
            return score

        # Filter Schemes
        scheme_results = []
        for _, row in self.schemes_df.iterrows():
            text = row['combined_text']
            score = 0
            
            # Occupation match (High weight)
            score += calculate_score(text, occ_keywords) * 2
            
            # Interest match
            score += calculate_score(text, interests)
            
            if score > 0:
                scheme = row.to_dict()
                # Clean up nan values for JSON serialization
                cleaned_scheme = {k: (v if pd.notna(v) else "") for k, v in scheme.items()}
                # Remove internal column
                if 'combined_text' in cleaned_scheme:
                    del cleaned_scheme['combined_text']
                cleaned_scheme['match_score'] = score
                scheme_results.append(cleaned_scheme)
        
        # Sort by score desc
        scheme_results.sort(key=lambda x: x['match_score'], reverse=True)

        # --- Job Matching ---
        job_results = []
        # Job keywords: Skills + Interests + Occupation
        job_keywords = skills + interests
        is_student = "student" in occupation or "graduating" in occupation or "fresher" in occupation

        if is_student:
             job_keywords += ["internship", "fresher", "entry", "scholarship", "training"]

        # heuristic to identify popular/general portals if no specific match
        # broadly known portals often have low IDs in this dataset (1-10) or specific names
        major_portals = ["naukri", "indeed", "linkedin", "monster", "glassdoor", "shine"]

        for _, row in self.jobs_df.iterrows():
            text = row['combined_text']
            score = 0
            
            # 1. Keyword Match
            score += calculate_score(text, job_keywords)
            
            # 2. Occupation Context Boost
            # If student, boost portals with 'fresher', 'intern', 'entry' in description
            if is_student and any(k in text for k in ["fresher", "intern", "entry", "training"]):
                score += 2

            # 3. Popularity/Fallback Boost
            # If keywords provided but no match found yet, we still want to show meaningful results.
            # Give a small base score to major portals so they appear if nothing else matches specific skills.
            if any(p in text for p in major_portals):
                score += 0.5

            # Always add the job, but sorting determines visibility
            job = row.to_dict()
            cleaned_job = {k: (v if pd.notna(v) else "") for k, v in job.items()}
            if 'combined_text' in cleaned_job:
                del cleaned_job['combined_text']
            
            cleaned_job['match_score'] = score
            job_results.append(cleaned_job)

        # Sort by score desc
        job_results.sort(key=lambda x: x['match_score'], reverse=True)

        return {
            "schemes": scheme_results[:50], 
            "jobs": job_results[:50]
        }

    def analyze_skill_gap(self, user_skills: list, target_role: str):
        # Force reload data to ensure we have the latest CSV content
        self.load_data()
        
        if self.jobs_df is None:
            return {"error": "Job data not loaded"}

        # 1. Normalize inputs
        target_role = target_role.lower().strip()
        user_skills_set = set([s.lower().strip() for s in user_skills if s.strip()])
        
        # 2. Extract Keywords & Synonyms
        import re
        # Remove punctuation
        clean_role = re.sub(r'[^\w\s]', ' ', target_role)
        keywords = set(k for k in clean_role.split() if len(k) > 1) # simple length filter
        
        # Add basic synonyms common in tech
        synonyms = {
            "developer": "development",
            "development": "developer",
            "engineer": "engineering",
            "engineering": "engineer",
            "admin": "administration",
            "administration": "admin",
            "manager": "management",
            "management": "manager",
            "web": "website"
        }
        
        expanded_keywords = set(keywords)
        for k in keywords:
            if k in synonyms:
                expanded_keywords.add(synonyms[k])
                
        print(f"DEBUG: Target Role: '{target_role}'")
        print(f"DEBUG: Search Keywords: {expanded_keywords}")

        # 3. Search for Relevant Jobs (Portals)
        # A row is relevant if ANY of its text columns contain ANY of the expanded keywords
        
        relevant_jobs = pd.DataFrame()
        
        if not self.jobs_df.empty:
            mask = pd.Series([False] * len(self.jobs_df))
            for kw in expanded_keywords:
                # Check domains (e.g. "Web Development" matched by "Developer")
                mask |= self.jobs_df['job_domains'].fillna('').str.lower().str.contains(kw, regex=False)
                # Check skills (e.g. "Java" matched by "Java")
                mask |= self.jobs_df['skill_requirements'].fillna('').str.lower().str.contains(kw, regex=False)
                # Check values like "Google"
                mask |= self.jobs_df['name'].fillna('').str.lower().str.contains(kw, regex=False)
            
            relevant_jobs = self.jobs_df[mask]
        
        print(f"DEBUG: Jobs/Portals Matched: {len(relevant_jobs)}")

        if relevant_jobs.empty:
            print("DEBUG: No relevant jobs found.")
            return {
                "role": target_role,
                "missing_skills": [],
                "matched_skills": [],
                "score": 0,
                "note": "No specific data found for this role."
            }

        # 4. Aggregate Required Skills
        required_skills_set = set()
        for skills_str in relevant_jobs['skill_requirements'].fillna(''):
            # skills_str is like "Python,Java,C++"
            skills = [s.strip().lower() for s in skills_str.split(',') if s.strip()]
            required_skills_set.update(skills)
            
        print(f"DEBUG: Required Skills: {required_skills_set}")
        
        # 5. Calculate Gap
        matched_skills = list(required_skills_set.intersection(user_skills_set))
        
        # Missing skills are those required but not in user's profile
        missing_skills = list(required_skills_set - user_skills_set)
        
        missing_skills.sort()
        matched_skills.sort()

        # Calculate Score
        total_required = len(required_skills_set)
        score = int((len(matched_skills) / total_required * 100)) if total_required > 0 else 0
        
        # Cap results for UI
        missing_skills_display = missing_skills[:12] # Top 12 missing

        # Generate Links
        missing_with_links = []
        for skill in missing_skills_display:
            query = f"learn {skill} course"
            link = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            course_link = f"https://www.classcentral.com/search?q={skill.replace(' ', '+')}"
            
            missing_with_links.append({
                "name": skill.title(), 
                "link": link,
                "course_link": course_link
            })

        return {
            "role": target_role,
            "missing_skills": missing_with_links,
            "matched_skills": [s.title() for s in matched_skills],
            "score": score
        }
