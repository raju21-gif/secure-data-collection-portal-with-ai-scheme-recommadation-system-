from recommendation_engine import RecommendationEngine
import json

def test_engine():
    print("Initializing Engine...")
    engine = RecommendationEngine()
    
    # Test Case 1: Student Interested in Technology
    profile1 = {
        "occupation": "Student",
        "skills": "Python, Java",
        "interest": "Technology, Coding",
        "location": "Delhi"
    }
    
    print(f"\nTesting Profile: {profile1}")
    results1 = engine.get_recommendations(profile1)
    
    print("\n--- Scheme Recommendations ---")
    for s in results1['schemes'][:3]:
        print(f"Name: {s['scheme_name']}, Score: {s['match_score']}, Type: {s['scheme_type']}")
        
    print("\n--- Job Recommendations ---")
    for j in results1['jobs'][:3]:
        print(f"Name: {j['name']}, Score: {j['match_score']}, Type: {j['type']}")

    # Test Case 2: Unemployed looking for anything
    profile2 = {
        "occupation": "Unemployed",
        "skills": "Driving",
        "interest": "Social Work",
        "location": "Mumbai"
    }
    
    print(f"\nTesting Profile: {profile2}")
    results2 = engine.get_recommendations(profile2)
    
    print("\n--- Scheme Recommendations ---")
    for s in results2['schemes'][:3]:
        print(f"Name: {s['scheme_name']}, Score: {s['match_score']}, Type: {s['scheme_type']}")

if __name__ == "__main__":
    test_engine()
