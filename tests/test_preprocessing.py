"""
Unit tests for text preprocessing and normalization.
"""

from src.preprocessing import clean_text, normalize_narrative, tokenize_narrative

def test_clean_text_handles_spaces_and_newlines():
    raw = "  Settlement  failed \n\n with custodian   DTC   "
    cleaned = clean_text(raw)
    assert cleaned == "Settlement failed with custodian DTC"

def test_clean_text_handles_none_and_non_strings():
    assert clean_text(None) == ""
    assert clean_text(12345) == ""

def test_normalize_narrative_lowercases_and_removes_stopwords():
    text = "The trade for ISIN US123456789 was rejected by the depository because of an error."
    normalized = normalize_narrative(text)
    # Stop words like 'the', 'for', 'was', 'by', 'of', 'an' should be removed
    tokens = normalized.split()
    assert "the" not in tokens
    assert "was" not in tokens
    assert "isin" in tokens
    assert "us123456789" in tokens
    assert "rejected" in tokens
    assert "depository" in tokens
    assert "error" in tokens

def test_tokenize_narrative_returns_list():
    tokens = tokenize_narrative("Custodian reported lack of cash in Nostro account")
    assert isinstance(tokens, list)
    assert "custodian" in tokens
    assert "cash" in tokens
    assert "nostro" in tokens

