import pandas as pd
import os
import time
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from dotenv import load_dotenv
from llm_client import call_llm

load_dotenv()

# Configuration
INPUT_FILE = "prompts.csv"
OUTPUT_FILE = "results.csv"

# List of models to test
# Gemini 1.5 Flash is highly stable and recommended
# HF models selected for high availability on free tier
MODELS = [
    "gemini-1.5-flash",
    "Qwen/Qwen2.5-7B-Instruct",
    "HuggingFaceH4/zephyr-7b-beta",
    "mistralai/Mistral-7B-Instruct-v0.2"
]

def preprocess_text(text):
    """Clean and tokenize text."""
    if not text:
        return ""
    # Remove extra spaces and newlines
    return " ".join(text.split())

def calculate_heuristics(text):
    """Calculate basic text metrics."""
    if not text:
        return {"word_count": 0, "sentence_count": 0, "avg_word_length": 0}
    
    words = word_tokenize(text)
    sentences = sent_tokenize(text)
    
    word_count = len(words)
    sentence_count = len(sentences)
    avg_word_length = sum(len(w) for w in words) / word_count if word_count > 0 else 0
    
    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_word_length": round(avg_word_length, 2)
    }

def run_pipeline():
    print(f"Loading prompts from {INPUT_FILE}...")
    try:
        # Read CSV - your file has many columns, we only need prompt_id and final_prompt
        df_prompts = pd.read_csv(INPUT_FILE)
        required_cols = ['prompt_id', 'final_prompt']
        for col in required_cols:
            if col not in df_prompts.columns:
                print(f"Error: CSV is missing required column: {col}")
                return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    results = []

    for _, row in df_prompts.iterrows():
        prompt_id = row['prompt_id']
        prompt_text = row['final_prompt']
        
        # Skip empty prompts
        if pd.isna(prompt_text) or str(prompt_text).strip() == "":
            continue

        for model in MODELS:
            print(f"--- Processing: {prompt_id} | Model: {model} ---")
            
            # 1. Call LLM
            generated_text = call_llm(model, prompt_text)
            
            if "ERROR" in generated_text:
                print(f"   [!] {generated_text}")
            
            # 2. Preprocess
            processed = preprocess_text(generated_text)
            
            # 3. Calculate Heuristics
            heuristics = calculate_heuristics(processed)
            
            # Store result with metadata from your CSV
            result_entry = {
                "prompt_id": prompt_id,
                "model": model,
                "generated_text": generated_text.replace("\n", " ") if generated_text else "",
                **heuristics
            }
            results.append(result_entry)
            
            # Rate limiting delay
            time.sleep(2)

    # Save to CSV
    if results:
        df_results = pd.DataFrame(results)
        df_results.to_csv(OUTPUT_FILE, index=False)
        print(f"Pipeline complete. Results saved to {OUTPUT_FILE}")
    else:
        print("No results generated.")

if __name__ == "__main__":
    # Ensure NLTK data is available
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    
    run_pipeline()
