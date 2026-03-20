import re

# Heuristic Keywords
KEYWORDS = {
    "support": ["support", "help", "assist", "aid", "grant", "funding", "subsidy"],
    "long_term": ["long-term", "future", "sustainable", "strategy", "vision", "planning"],
    "risk": ["risk", "uncertainty", "danger", "threat", "hazard", "volatility"]
}

def calculate_heuristics(processed_data):
    """Calculates the 6 heuristic indices."""
    tokens = processed_data["tokens"]
    sentences = processed_data["sentences"]
    raw_text = processed_data["raw"]
    
    # Count options (numbered lists or bullet points)
    option_count = len(re.findall(r'\d+\.|\*|-', raw_text))
    
    # Keyword counts
    support_count = sum(1 for t in tokens if t in KEYWORDS["support"])
    long_term_count = sum(1 for t in tokens if t in KEYWORDS["long_term"])
    risk_count = sum(1 for t in tokens if t in KEYWORDS["risk"])
    
    return {
        "token_count": len(tokens),
        "sentence_count": len(sentences),
        "option_count": option_count,
        "support_option_count": support_count,
        "long_term_keyword_count": long_term_count,
        "risk_keyword_count": risk_count
    }
