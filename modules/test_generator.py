import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables (.env file)
load_dotenv()

class AITestGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("Warning: OPENAI_API_KEY is missing. Please add it to your .env file.")
        else:
            self.client = OpenAI(api_key=self.api_key)

    def generate_test_cases(self, requirement_text: str):
        """
        Generates functional, negative, and edge-case test scenarios from software requirements.
        """
        if not self.api_key:
            return {"error": "API Key missing. Please configure OPENAI_API_KEY."}

        prompt = f"""
        You are an expert QA Automation Engineer.
        Analyze the following software requirements and generate structured test cases.

        REQUIREMENTS:
        {requirement_text}

        Return the response strictly as a JSON object with this format:
        {{
            "feature": "Name of feature",
            "test_cases": [
                {{
                    "id": "TC001",
                    "title": "Title of test case",
                    "type": "Functional / Negative / Edge Case",
                    "steps": ["Step 1", "Step 2"],
                    "expected_result": "Expected outcome"
                }}
            ]
        }}
        Do not include markdown or extra text outside the JSON.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            
            raw_result = response.choices[0].message.content.strip()
            
            # Clean markdown code blocks if present
            if raw_result.startswith("```json"):
                raw_result = raw_result.replace("```json", "").replace("```", "").strip()

            return json.loads(raw_result)

        except Exception as e:
            return {"error": f"Failed to generate test cases: {str(e)}"}

# Test module execution locally
if __name__ == "__main__":
    req_file_path = os.path.join("data", "sample_requirements.txt")
    
    if os.path.exists(req_file_path):
        with open(req_file_path, "r") as f:
            sample_req = f.read()

        generator = AITestGenerator()
        print("Generating test cases using AI...")
        result = generator.generate_test_cases(sample_req)
        print("\n--- GENERATED TEST SUITE ---")
        print(json.dumps(result, indent=2))
    else:
        print(f"Sample requirements file not found at: {req_file_path}")

       