import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini if key is present
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def call_gemini(model_id, prompt):
    """Calls the Google Gemini API."""
    try:
        model = genai.GenerativeModel(model_id)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"ERROR Gemini: {str(e)}"

def call_huggingface(model_id, prompt):
    """Calls the Hugging Face Inference API using the OpenAI-compatible endpoint."""
    # This endpoint is generally more stable than the model-specific ones
    api_url = "https://api-inference.huggingface.co/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 401:
            return "ERROR HF: Invalid API Key."
        if response.status_code == 429:
            return "ERROR HF: Rate limit exceeded."
        if response.status_code == 404:
            return f"ERROR HF: Model {model_id} not found."
            
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        return ""
    except Exception as e:
        return f"ERROR HF: {str(e)}"

def call_llm(model_id, prompt):
    """Unified caller for Gemini and Hugging Face."""
    if "gemini" in model_id.lower():
        return call_gemini(model_id, prompt)
    else:
        return call_huggingface(model_id, prompt)
