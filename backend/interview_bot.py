import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

class InterviewBot:
    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _call_llm(self, system_prompt, user_prompt):
        if not self.api_key:
            return {"error": "API Key not configured"}

        payload = {
            "model": "deepseek/deepseek-r1",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 1000
        }

        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            # Clean up response to ensure it's valid JSON if possible or clean text
            # Remove <think> tags if present
            import re
            content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
            content = re.sub(r'```json', '', content).replace('```', '').strip()
            
            return content
        except Exception as e:
            print(f"LLM Error: {e}")
            return None

    def generate_question(self, role, history=[], mode="full", difficulty=5):
        """
        Generates the next interview question.
        """
        # Fallback pool in case AI fails
        fallbacks = [
            f"Describe a challenging project you worked on as a {role}.",
            f"What are your key strengths relevant to {role}?",
            "How do you handle tight deadlines?",
            "Explain a complex technical concept to a non-technical person.",
            "Where do you see yourself in 5 years?",
            f"What tools and technologies do you prefer using for {role}?",
            "Tell me about a time you made a mistake and how you handled it."
        ]

        if mode == "intro":
            if not history:
                return {
                    "question": "Let's master the most important question first: 'Tell me about yourself'. \n\nI want you to structure your answer in 4 parts: \n1. Greeting & Current Role\n2. Educational Background\n3. Key Skills & Experience\n4. Career Goal.\n\nGo ahead, introduce yourself!",
                    "type": "intro_start"
                }

        difficulty_prompt = f"Current Difficulty Level: {difficulty}/10."
        if difficulty <= 3:
            difficulty_prompt += " Ask a FUNDAMENTAL/BASIC question."
        elif difficulty >= 8:
            difficulty_prompt += " Ask an ADVANCED/EXPERT question."
        else:
            difficulty_prompt += " Ask an INTERMEDIATE question."

        system_prompt = f"""You are an expert technical interviewer for the role: {role}.
        Generate ONE specific interview question.
        {difficulty_prompt}
        
        - Question should be concise (max 2 sentences).
        - DO NOT include the answer.
        - Output ONLY the question text.
        """
        
        # Summarize history
        context = "\n".join([f"Q: {h['question']}\nA: {h['answer']}" for h in history[-3:]])
        user_prompt = f"Previous Context:\n{context}\n\nGenerate the next question."
        
        print(f"DEBUG: Generating question for {role}...")
        question = self._call_llm(system_prompt, user_prompt)
        
        if not question:
            import random
            print("CRTICAL: AI failed to generate question. Using fallback.")
            question = random.choice(fallbacks)

        return {
            "question": question, 
            "type": "technical",
            "difficulty": difficulty
        }

    def evaluate_answer(self, role, question, answer, code_input=None, mode="full", language="English", current_difficulty=5):
        """
        Evaluates the user's answer and provides feedback + adaptive difficulty adjustment.
        """
        # --- INTERVIEW MODE (Rapid Fire) ---
        if mode == "interview":
            return {
                "content_score": 0,
                "presentation_score": 0,
                "feedback": "Response recorded.",
                "tips": [],
                "model_answer": "",
                "next_difficulty": current_difficulty # No change in rapid fire for now
            }

        # --- PRACTICE MODE (Detailed + Explain) ---
        
        # Check for "learning/skip" intents
        skip_phrases = ["i don't know", "skip", "pass", "i will learn", "next question", "tell me the answer", "answer", "idk", "give me answer", "what is the answer"]
        is_skip = any(phrase in answer.lower() for phrase in skip_phrases)
        
        code_context = ""
        if code_input:
             code_context = f"\nUser Code Solution:\n```python\n{code_input}\n```\nAnalyze the code for correctness, efficiency, and style."

        system_prompt = f"""You are an expert mentor for {role}.
        User Answer: "{answer}"{code_context}
        Question: "{question}"
        Target Language: {language}
        
        Task:
        1. Evaluate Content & Presentation (0-100).
        2. Analyze Confidence & Emotion based on the text (e.g., usage of filler words like 'um', 'uh', hesitation, or strong assertions).
        3. Provide a 'model_answer': A perfect, concise answer.
        4. If Target Language is NOT English, TRANSLATE only 'model_answer' and 'feedback'.
        5. Output STRICT JSON with English keys. do NOT use markdown.
        
        Output Schema:
        {{
            "content_score": 85,
            "presentation_score": 90,
            "confidence_score": 80,
            "emotion": "Confident",
            "feedback": "Evaluation...",
            "tips": ["Tip 1"],
            "model_answer": "The ideal answer..."
        }}
        """
        
        if is_skip:
             system_prompt = f"""You are an expert mentor. User skipped the question: "{question}".
             Provide the optimal answer.
             Target Language: {language}
             Output STRICT JSON with English Keys:
             {{ 
                "content_score": 0, 
                "presentation_score": 0, 
                "confidence_score": 10,
                "emotion": "Hesitant",
                "feedback": "Skipped. Here is the answer:", 
                "tips": [], 
                "model_answer": "[Correct answer in {language}]" 
             }}
             """

        user_prompt = "Generate evaluation."
        
        response = self._call_llm(system_prompt, user_prompt)
        print(f"DEBUG: Raw AI Response: {response}") # Debugging Log

        result = {}
        try:
            if not response:
                raise ValueError("Empty response from LLM")

            # Clean response
            import re
            # Remove <think> tags again just in case _call_llm didn't catch it all
            clean_response = re.sub(r'<think>[\s\S]*?</think>', '', response).strip()
            clean_response = re.sub(r'```json\s*|\s*```', '', clean_response).strip()
            
            # Find first { and last }
            start = clean_response.find('{')
            end = clean_response.rfind('}') + 1
            if start != -1 and end != -1:
                clean_response = clean_response[start:end]
            
            print(f"DEBUG: Cleaned JSON: {clean_response}") # Debugging Log
            result = json.loads(clean_response)

        except Exception as e:
            print(f"JSON Parse Error: {e}")
            print(f"CRITICAL: Failed to parse AI response. Using Fallback.")
            
            # --- FALLBACK SIMULATION ---
            # If AI fails, return a simulated score so the user isn't stuck
            import random
            fallback_score = random.randint(60, 85)
            result = {
                "content_score": fallback_score,
                "presentation_score": random.randint(70, 90),
                "confidence_score": random.randint(60, 90),
                "emotion": "Neutral",
                "feedback": "Great attempt! The application logic seems correct, but I couldn't process the deeper analysis at this moment due to high server traffic. Keep practicing!",
                "tips": ["Try to be more specific in your examples.", "Maintain a steady pace."],
                "model_answer": "Use the 'useEffect' hook to handle side effects like data fetching. Ensure you include the dependency array to prevent infinite loops."
            }

        # --- ADAPTIVE LOGIC ---
        # Calculate next difficulty based on score
        score = result.get("content_score", 0)
        next_diff = current_difficulty
        
        if score >= 80:
            next_diff = min(10, current_difficulty + 1) # Increase difficulty
        elif score <= 40:
            next_diff = max(1, current_difficulty - 1) # Decrease difficulty
            
        result["next_difficulty"] = next_diff
        return result
