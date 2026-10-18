"""
Unit tests for Approach B: TF-IDF lexical retrieval.
"""

from src.lexical_retrieval import LexicalRetriever, load_procedure_documents

def test_load_procedure_documents():
    """Verify that all markdown procedure files are loaded and parsed."""
    docs = load_procedure_documents()
    assert len(docs) >= 12, f"Expected at least 12 procedure documents, found {len(docs)}"
    for doc in docs:
        assert doc["procedure_id"].startswith("PROC_")
        assert len(doc["title"]) > 0
        assert len(doc["clean_text"]) > 0
        assert doc["category"] != "UNKNOWN"

def test_lexical_retriever_ranking():
    """Verify lexical retriever returns Top-3 relevant results with descending scores."""
    retriever = LexicalRetriever()
    assert retriever.is_ready

    query = "Safekeeping account mismatch on settlement instruction with custodian"
    results = retriever.retrieve(query, top_k=3)
    assert len(results) == 3
    assert results[0]["procedure_id"] in ["PROC_01", "PROC_02"]
    assert results[0]["score"] >= results[1]["score"] >= results[2]["score"]

def test_lexical_retriever_empty_query():
    """Verify empty query returns empty list gracefully."""
    retriever = LexicalRetriever()
    results = retriever.retrieve("", top_k=3)
    assert results == []

from unittest.mock import MagicMock
from src.semantic_retrieval import SemanticRetriever
from src.embedding_index import ProcedureVectorIndex

def test_embedding_retrieval_with_mocked_inference():
    """Verify semantic retrieval flow with mocked OllamaClient embeddings."""
    mock_ollama = MagicMock()
    mock_ollama.get_embeddings.return_value = [[0.05] * 768]

    mock_collection = MagicMock()
    mock_collection.count.return_value = 10
    mock_collection.query.return_value = {
        "documents": [["Procedure PROC_01: Verify SSI account consistency."]],
        "metadatas": [[{
            "procedure_id": "PROC_01",
            "title": "Verify SSI",
            "category": "SSI_MISMATCH",
            "source_type": "Synthetic",
            "section_type": "full",
        }]],
        "distances": [[0.25]]
    }

    mock_index = MagicMock(spec=ProcedureVectorIndex)
    mock_index.is_indexed.return_value = True
    mock_index.collection = mock_collection

    retriever = SemanticRetriever(vector_index=mock_index, ollama_client=mock_ollama)
    results = retriever.retrieve("Safekeeping account mismatch", top_k=1)

    assert len(results) == 1
    assert results[0]["procedure_id"] == "PROC_01"
    assert results[0]["similarity_score"] > 0.8
    assert results[0]["category"] == "SSI_MISMATCH"

def test_persistent_index_metadata_structure():
    """Verify that chunk_procedure_document preserves all required metadata attributes."""
    from src.embedding_index import chunk_procedure_document
    doc = {
        "procedure_id": "PROC_99",
        "title": "Mock Procedure",
        "category": "SETTLEMENT_TIMING",
        "source_type": "Synthetic Guidance",
        "raw_text": "## Trigger Indicators\nLate batch.\n## Generic Verification Steps\nCheck timetable.\n## Missing Information\nLogs."
    }
    chunks = chunk_procedure_document(doc)
    assert len(chunks) >= 2
    for chunk in chunks:
        assert chunk["procedure_id"] == "PROC_99"
        assert chunk["category"] == "SETTLEMENT_TIMING"
        assert chunk["title"] == "Mock Procedure"
        assert chunk["source_type"] == "Synthetic Guidance"
        assert "section_type" in chunk
        assert len(chunk["text"]) > 0

