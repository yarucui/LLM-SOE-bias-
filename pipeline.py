import time
import pandas as pd
from llm_client import call_llm
from preprocessing import preprocess_text
from heuristics import calculate_heuristics

# Configuration
INPUT_FILE = "prompts.csv"
OUTPUT_FILE = "results.csv"

# List of models to test
# Gemini models are highly recommended for reliability
# HF models use the newer chat/completions endpoint
MODELS = [
    "gemini-1.5-flash",
    "google/gemma-2-2b-it",
    "HuggingFaceH4/zephyr-7b-beta",
    "mistralai/Mistral-7B-Instruct-v0.2"
]

def run_pipeline():
    print(f"Loading prompts from {INPUT_FILE}...")
    try:
        # Read CSV and ensure we only take the necessary columns
        df_prompts = pd.read_csv(INPUT_FILE)
        if 'prompt_id' not in df_prompts.columns or 'final_prompt' not in df_prompts.columns:
            print("Error: CSV must contain 'prompt_id' and 'final_prompt' columns.")
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
            
            if "ERROR:" in generated_text:
                print(f"   [!] {generated_text}")
            
            # 2. Preprocess
            processed = preprocess_text(generated_text)
            
            # 3. Calculate Heuristics
            heuristics = calculate_heuristics(processed)
            
            # Store result
            result_entry = {
                "prompt_id": prompt_id,
                "model": model,
                "generated_text": generated_text.replace("\n", " "), # Flatten for CSV
                **heuristics
            }
            results.append(result_entry)
            
            # Rate limiting delay (HF free tier requires some breathing room)
            time.sleep(2)

    # Save to CSV
    df_results = pd.DataFrame(results)
    df_results.to_csv(OUTPUT_FILE, index=False)
    print(f"Pipeline complete. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_pipeline()
