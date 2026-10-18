"""
Text preprocessing and normalization module for SettleSense.
Provides clean tokenization, text normalization, and input sanitation
for financial exception narratives.
"""

import re
import string
from typing import List

# Standard English stop words customized to preserve key financial transaction terms
FINANCIAL_STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}

def clean_text(text: str) -> str:
    """
    Cleans and standardizes raw input text:
    - Strips whitespace
    - Normalizes multiple spaces and newlines
    - Removes unprintable characters
    """
    if not isinstance(text, str):
        return ""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text

def normalize_narrative(text: str) -> str:
    """
    Performs case normalization, punctuation filtering, and stop-word pruning.
    Returns cleaned, space-separated normalized string.
    """
    cleaned = clean_text(text).lower()
    # Replace punctuation with spaces except hyphens inside identifiers
    cleaned = re.sub(r"[^\w\s\-]", " ", cleaned)
    tokens = cleaned.split()
    filtered_tokens = [t for t in tokens if t not in FINANCIAL_STOP_WORDS and len(t) > 1]
    return " ".join(filtered_tokens)

def tokenize_narrative(text: str) -> List[str]:
    """Tokenizes narrative into list of normalized terms."""
    return normalize_narrative(text).split()

