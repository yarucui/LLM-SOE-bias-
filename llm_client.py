import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")

def call_llm(model_id, prompt):
    """Calls the Hugging Face Inference API."""
    if not HF_API_KEY:
        raise ValueError("HF_API_KEY not found in environment.")

    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 500, "return_full_text": False}
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 410:
            return f"ERROR: Model {model_id} is no longer available (410 Gone)."
        if response.status_code == 401:
            return "ERROR: Invalid HF_API_KEY. Please check your .env file."
        if response.status_code == 429:
            return "ERROR: Rate limit exceeded. Try increasing the sleep time."
            
        response.raise_for_status()
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "")
        elif isinstance(result, dict) and "generated_text" in result:
            return result["generated_text"]
        return ""
    except requests.exceptions.Timeout:
        return "ERROR: Request timed out."
    except Exception as e:
        return f"ERROR: {str(e)}"
