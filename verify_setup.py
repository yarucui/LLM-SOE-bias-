import os
from llm_client import call_llm
from dotenv import load_dotenv

load_dotenv()

def verify():
    print("--- Verifying API Connectivity ---")
    
    # Test models
    models_to_test = [
        "gemini-1.5-flash",
        "Qwen/Qwen2.5-7B-Instruct"
    ]
    
    for model in models_to_test:
        print(f"Testing {model}...")
        result = call_llm(model, "Hello, say 'Ready' if you can hear me.")
        if "ERROR" in result:
            print(f"   [!] FAILED: {result}")
        else:
            print(f"   [+] SUCCESS: {result[:50]}...")

if __name__ == "__main__":
    verify()
