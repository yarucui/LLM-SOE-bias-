import re

def preprocess_text(text):
    """Cleans and tokenizes text."""
    # Clean special characters (keep basic punctuation)
    cleaned = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', text)
    
    # Tokenize (lowercase and split)
    tokens = cleaned.lower().split()
    
    # Segment into sentences
    sentences = [s.strip() for s in re.split(r'[.!?]', cleaned) if s.strip()]
    
    return {
        "raw": text,
        "tokens": tokens,
        "sentences": sentences
    }
