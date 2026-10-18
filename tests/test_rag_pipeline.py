"""
Unit tests for Approach C and Approach D RAG pipeline with mocked LLM generation.
"""

import json
from unittest.mock import MagicMock
from src.rag_pipeline import (
    SettleSenseRAGPipeline,
    build_prompt_only_prompt,
    build_rag_prompt,
)
from src.ollama_client import OllamaClient, OllamaServiceError

MOCK_VALID_REPORT = {
    "case_id": "TEST-01",
    "case_summary": "Cash deficit in Nostro account prevented DvP settlement.",
    "candidate_failure_category": "CASH_SHORTFALL",
    "category_confidence_or_uncertainty": "HIGH",
    "supporting_evidence": ["Nostro balance was $12,000 against required $450,000 consideration."],
    "possible_causes": ["Incoming FX wire delayed at correspondent bank."],
    "recommended_checks": ["Review Nostro intraday ledger using PROC_07."],
    "missing_information": ["SWIFT GPI payment tracking status."],
    "procedure_references": ["PROC_07"],
    "investigation_note": "Coordinate with treasury for liquidity injection.",
    "requires_human_review": True,
}

def test_prompt_builders():
    """Verify prompt formatting for prompt-only and RAG."""
    p_only = build_prompt_only_prompt(
        case_description="Trade failed at depository due to timing cutoff.",
        case_id="CASE-01"
    )
    assert "CASE-01" in p_only
    assert "Allowed Categories:" in p_only

    retrieved = [{
        "procedure_id": "PROC_12",
        "title": "Cutoff Timing",
        "category": "SETTLEMENT_TIMING",
        "passage_text": "Verify depository batch release cutoffs."
    }]
    p_rag = build_rag_prompt(
        case_description="Late batch release exception.",
        retrieved_procedures=retrieved,
        case_id="CASE-02"
    )
    assert "PROC_12" in p_rag
    assert "RETRIEVED PROCEDURE EVIDENCE:" in p_rag

def test_rag_pipeline_with_mocked_success():
    """Verify successful RAG execution and report validation using mocked LLM."""
    mock_ollama = MagicMock(spec=OllamaClient)
    mock_ollama.generate.return_value = {
        "response": json.dumps(MOCK_VALID_REPORT)
    }

    mock_retriever = MagicMock()
    mock_retriever.is_ready = True
    mock_retriever.retrieve.return_value = [{
        "procedure_id": "PROC_07",
        "title": "Verify Cash",
        "category": "CASH_SHORTFALL",
        "passage_text": "Check Nostro balance."
    }]

    pipeline = SettleSenseRAGPipeline(
        ollama_client=mock_ollama,
        semantic_retriever=mock_retriever
    )

    result = pipeline.run_rag(
        case_description="Nostro account had insufficient cash to settle bond purchase.",
        case_id="TEST-01"
    )

    assert result["success"] is True
    assert result["report"] is not None
    assert result["report"].candidate_failure_category == "CASH_SHORTFALL"
    assert "PROC_07" in result["report"].procedure_references
    assert len(result["retrieved_procedures"]) == 1

def test_rag_pipeline_handles_offline_ollama_gracefully():
    """Verify that when Ollama raises connection error, pipeline returns safe fallback."""
    mock_ollama = MagicMock(spec=OllamaClient)
    mock_ollama.generate.side_effect = OllamaServiceError("Connection refused at http://localhost:11434")

    mock_retriever = MagicMock()
    mock_retriever.is_ready = False

    pipeline = SettleSenseRAGPipeline(
        ollama_client=mock_ollama,
        semantic_retriever=mock_retriever
    )

    result = pipeline.run_rag(
        case_description="Some settlement exception narrative.",
        case_id="ERR-01"
    )

    assert result["success"] is False
    assert result["report"] is not None
    assert result["report"].candidate_failure_category == "UNDETERMINED"
    assert result["report"].requires_human_review is True
    assert "Connection refused" in result["error"]

def test_prompt_only_pipeline_with_mocked_success():
    """Verify prompt-only inference pipeline with mocked LLM."""
    mock_ollama = MagicMock(spec=OllamaClient)
    mock_ollama.generate.return_value = {
        "response": json.dumps(MOCK_VALID_REPORT)
    }

    pipeline = SettleSenseRAGPipeline(ollama_client=mock_ollama)
    result = pipeline.run_prompt_only(
        case_description="Cash shortage on settlement.",
        case_id="TEST-01"
    )
    assert result["success"] is True
    assert result["report"].candidate_failure_category == "CASH_SHORTFALL"
    assert result["retrieved_procedures"] == []

from src.ollama_client import OllamaModelNotFoundError

def test_missing_local_model_error():
    """Verify handling when specified model tag is not found locally."""
    mock_ollama = MagicMock(spec=OllamaClient)
    mock_ollama.generate.side_effect = OllamaModelNotFoundError("Model 'nonexistent:model' not found.")

    pipeline = SettleSenseRAGPipeline(ollama_client=mock_ollama)
    result = pipeline.run_rag("Some narrative", case_id="CASE-NOMODEL")
    assert result["success"] is False
    assert result["report"].candidate_failure_category == "UNDETERMINED"
    assert result["report"].requires_human_review is True
    assert "not found" in result["error"].lower()

def test_rag_pipeline_with_empty_retrieved_documents():
    """Verify RAG pipeline functions safely when semantic retrieval returns empty results."""
    mock_ollama = MagicMock(spec=OllamaClient)
    mock_ollama.generate.return_value = {
        "response": json.dumps(MOCK_VALID_REPORT)
    }

    mock_retriever = MagicMock()
    mock_retriever.is_ready = True
    mock_retriever.retrieve.return_value = []

    pipeline = SettleSenseRAGPipeline(
        ollama_client=mock_ollama,
        semantic_retriever=mock_retriever
    )
    result = pipeline.run_rag("Rare exception without procedure matches", case_id="CASE-NO-PROC")
    assert result["report"] is not None
    assert result["retrieved_procedures"] == []

def test_rag_pipeline_with_irrelevant_procedures():
    """Verify RAG pipeline handles irrelevant retrieved procedures safely."""
    from src.output_validation import verify_evidence_support
    mock_ollama = MagicMock(spec=OllamaClient)
    # LLM hallucinates an irrelevant procedure citation
    report_with_irrelevant = dict(MOCK_VALID_REPORT)
    report_with_irrelevant["procedure_references"] = ["PROC_01"] # SSI procedure for cash shortfall
    mock_ollama.generate.return_value = {
        "response": json.dumps(report_with_irrelevant)
    }

    mock_retriever = MagicMock()
    mock_retriever.is_ready = True
    # Retrieved procedure is unrelated to cash shortfall
    mock_retriever.retrieve.return_value = [{
        "procedure_id": "PROC_01",
        "title": "Safekeeping SSI Verification",
        "category": "SSI_MISMATCH",
        "passage_text": "Verify depository safekeeping account numbers and SSI profiles."
    }]

    pipeline = SettleSenseRAGPipeline(
        ollama_client=mock_ollama,
        semantic_retriever=mock_retriever
    )
    result = pipeline.run_rag(
        case_description="Nostro account had insufficient funds to settle bond transaction.",
        case_id="IRREL-01"
    )
    assert result["success"] is True
    assert result["report"] is not None
    assert "PROC_01" in [p["procedure_id"] for p in result["retrieved_procedures"]]

def test_rag_pipeline_evidence_support_verification():
    """Verify evidence support checking catches hallucinated details."""
    from src.output_validation import verify_evidence_support
    case_desc = "Account SAFEKEEP-1021 rejected due to mismatch with counterparty DEP-20412."
    passages = ["Procedure PROC_01 states that safekeeping accounts must be re-verified."]
    
    # Supported claims
    supported_claims = [
        "Internal safekeeping account SAFEKEEP-1021 mismatch detected.",
        "Counterparty account DEP-20412 was rejected."
    ]
    rate, unsupported = verify_evidence_support(supported_claims, case_desc, passages)
    assert rate == 1.0
    assert len(unsupported) == 0

    # Hallucinated claims
    hallucinated_claims = [
        "Internal safekeeping account SAFEKEEP-1021 mismatch detected.",
        "Total unhedged collateral deficit was 985,000,000 Yen with Tokyo branch."
    ]
    rate, unsupported = verify_evidence_support(hallucinated_claims, case_desc, passages)
    assert rate < 1.0
    assert len(unsupported) == 1
    assert "985,000,000" in unsupported[0]


def test_rag_pipeline_hard_timeout_interruption():
    """Verify that a deliberately slow/stalled LLM request is interrupted and caught as TIMEOUT_FALLBACK."""
    mock_ollama = MagicMock(spec=OllamaClient)
    def _slow_generate(*args, **kwargs):
        raise OllamaTimeoutError("Ollama call exceeded client deadline of 0.1s (elapsed: 0.10s)")
    mock_ollama.generate.side_effect = _slow_generate

    mock_retriever = MagicMock()
    mock_retriever.is_ready = False

    pipeline = SettleSenseRAGPipeline(
        ollama_client=mock_ollama,
        semantic_retriever=mock_retriever
    )
    result = pipeline.run_rag(
        case_description="Delayed settlement timing exception.",
        case_id="TIMEOUT-01",
        timeout=0.1,
    )
    assert result["generation_status"] == "TIMEOUT_FALLBACK"
    assert result["is_fallback"] is True
    assert result["success"] is False
    assert result["report"].candidate_failure_category == "UNDETERMINED"
    assert result["report"].requires_human_review is True
    assert result["validation"].evidence_support_rate == 0.0


