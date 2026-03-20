# Python Research Pipeline

This pipeline automates LLM model iteration, text preprocessing, and heuristic calculation for research purposes.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure API Key:**
    Open the `.env` file and replace `your_hugging_face_api_key_here` with your actual Hugging Face API key. You can get one for free at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).

3.  **Prepare Prompts:**
    Ensure `prompts.csv` is in the root directory with the format:
    `prompt_id,final_prompt`

## Running the Pipeline

Execute the main script:
```bash
python pipeline.py
```

## Output

The script will generate a `results.csv` file containing:
*   `prompt_id`: The ID of the prompt.
*   `model`: The model used.
*   `generated_text`: The raw output from the LLM.
*   `token_count`: Total number of tokens.
*   `sentence_count`: Total number of sentences.
*   `option_count`: Number of detected list items/options.
*   `support_option_count`: Count of keywords related to financial support.
*   `long_term_keyword_count`: Count of keywords related to long-term goals.
*   `risk_keyword_count`: Count of keywords related to risk.
