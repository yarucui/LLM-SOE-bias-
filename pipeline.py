import time
import pandas as pd
from llm_client import call_llm
from preprocessing import preprocess_text
from heuristics import calculate_heuristics

# Configuration
INPUT_FILE = "prompts.csv"
OUTPUT_FILE = "results.csv"

# List of models to test (Hugging Face IDs)
MODELS = [
    "meta-llama/Llama-2-7b-chat-hf",
    "mistralai/Mistral-7B-v0.1",
    "tiiuae/falcon-7b-instruct"
]

def run_pipeline():
    print(f"Loading prompts from {INPUT_FILE}...")
    try:
        df_prompts = pd.read_csv(INPUT_FILE)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    results = []

    for _, row in df_prompts.iterrows():
        prompt_id = row['prompt_id']
        prompt_text = row['final_prompt']
        
        for model in MODELS:
            print(f"Processing Prompt {prompt_id} with {model}...")
            
            # 1. Call LLM
            generated_text = call_llm(model, prompt_text)
            
            # 2. Preprocess
            processed = preprocess_text(generated_text)
            
            # 3. Calculate Heuristics
            heuristics = calculate_heuristics(processed)
            
            # Store result
            result_entry = {
                "prompt_id": prompt_id,
                "model": model,
                "generated_text": generated_text,
                **heuristics
            }
            results.append(result_entry)
            
            # Rate limiting delay
            time.sleep(1)

    # Save to CSV
    df_results = pd.DataFrame(results)
    df_results.to_csv(OUTPUT_FILE, index=False)
    print(f"Pipeline complete. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_pipeline()
