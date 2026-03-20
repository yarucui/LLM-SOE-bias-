import os
from google import genai
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

# API Keys
HF_API_KEY = os.getenv("HF_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Clients
gemini_client = None
if GEMINI_API_KEY:
    # The new google-genai SDK handles API versions automatically
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)

hf_client = None
if HF_API_KEY:
    # InferenceClient is the official way to call HF models
    hf_client = InferenceClient(api_key=HF_API_KEY)

def call_gemini(model_id, prompt):
    """Calls the Google Gemini API using the new google-genai SDK."""
    if not gemini_client:
        return "ERROR Gemini: API Key not configured."
    try:
        # Use the standard model name (e.g., "gemini-1.5-flash")
        response = gemini_client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"ERROR Gemini: {str(e)}"

def call_huggingface(model_id, prompt):
    """Calls the Hugging Face Inference API using the official hub client."""
    if not hf_client:
        return "ERROR HF: API Key not configured."
    try:
        # Using the chat completion endpoint for Instruct models
        response = hf_client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        # Fallback to standard text generation if chat is not supported
        try:
            response = hf_client.text_generation(
                model=model_id,
                prompt=f"User: {prompt}\nAssistant:",
                max_new_tokens=500
            )
            return response
        except Exception as e2:
            return f"ERROR HF: {str(e)}"

def call_llm(model_id, prompt):
    """Unified caller for Gemini and Hugging Face."""
    if "gemini" in model_id.lower():
        return call_gemini(model_id, prompt)
    else:
        return call_huggingface(model_id, prompt)
