import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def predict_risk(code_diff_or_change: str, existing_tests: str) -> str:
    """
    Analyzes code changes/commits and predicts high-risk areas
    and which test cases must be prioritized.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    You are an AI QA Risk Predictor. Analyze the following recent code change/commit summary 
    against our existing test suite.

    Recent Code Changes:
    {code_diff_or_change}

    Existing Test Suite / Requirements:
    {existing_tests}

    Provide a structured output with:
    1. Risk Level (High / Medium / Low) with a percentage score.
    2. Vulnerable Modules likely impacted by this change.
    3. Prioritized Test Cases to run immediately (Predictive Test Selection).
    4. Suggested New Edge-Case Tests to add.
    """
    
    response = model.generate_content(prompt)
    return response.text