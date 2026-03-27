import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

def get_llm_explanation(prompt: str) -> str:
    """Wrapper to call Gemini 1.5 Flash."""
    if not GOOGLE_API_KEY:
        return "Explanation unavailable: Missing GOOGLE_API_KEY in .env."
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating explanation: {e}"