"""
Unit tests for output schemas, Pydantic validation, and citation checking.
"""

import json
from src.output_schemas import SettlementInvestigationReport
from src.output_validation import (
    validate_report,
    extract_json_from_llm_response,
    get_known_procedure_ids,
)

SAMPLE_VALID_REPORT = {
    "case_id": "SS-0001",
    "case_summary": "Depository rejected instruction due to safekeeping account mismatch.",
    "candidate_failure_category": "SSI_MISMATCH",
    "category_confidence_or_uncertainty": "HIGH",
    "supporting_evidence": ["Internal safekeeping account SAFEKEEP-1021 does not match counterparty DEP-20412."],
    "possible_causes": ["Counterparty updated SSI standing instructions without internal profile update."],
    "recommended_checks": ["Review depository account on master SSI database using PROC_01."],
    "missing_information": ["Signed SSI amendment confirmation."],
    "procedure_references": ["PROC_01", "PROC_02"],
    "investigation_note": "Risk is low if corrected before next CSD cycle.",
    "requires_human_review": True,
}

def test_valid_pydantic_report():
    """Verify clean instantiation of SettlementInvestigationReport."""
    report = SettlementInvestigationReport(**SAMPLE_VALID_REPORT)
    assert report.case_id == "SS-0001"
    assert report.candidate_failure_category == "SSI_MISMATCH"
    assert report.category_confidence_or_uncertainty == "HIGH"
    assert "PROC_01" in report.procedure_references

def test_invalid_category_rejected():
    """Verify invalid category raises validation error."""
    invalid_dict = dict(SAMPLE_VALID_REPORT)
    invalid_dict["candidate_failure_category"] = "INVALID_FABRICATED_CATEGORY"
    res = validate_report(invalid_dict)
    assert not res.is_valid
    assert len(res.validation_errors) > 0

def test_undetermined_enforces_human_review():
    """Verify UNDETERMINED automatically forces requires_human_review to True."""
    undetermined_dict = dict(SAMPLE_VALID_REPORT)
    undetermined_dict["candidate_failure_category"] = "UNDETERMINED"
    undetermined_dict["requires_human_review"] = False
    report = SettlementInvestigationReport(**undetermined_dict)
    assert report.requires_human_review is True

def test_citation_validation_detects_hallucinations():
    """Verify that nonexistent procedure IDs are flagged."""
    hallucinated_dict = dict(SAMPLE_VALID_REPORT)
    hallucinated_dict["procedure_references"] = ["PROC_01", "PROC_99", "REG_RULE_12"]
    known_ids = {"PROC_01", "PROC_02"}

    res = validate_report(hallucinated_dict, known_proc_ids=known_ids)
    assert not res.is_valid
    assert "PROC_99" in res.invalid_citations
    assert "REG_RULE_12" in res.invalid_citations
    assert "PROC_01" in res.valid_citations
    assert res.citation_validity_rate < 0.5

def test_extract_json_from_llm_markdown():
    """Verify extract_json_from_llm_response extracts JSON from markdown fences."""
    raw = f"Here is the investigation:\n```json\n{json.dumps(SAMPLE_VALID_REPORT)}\n```\nHope this helps!"
    extracted = extract_json_from_llm_response(raw)
    assert extracted is not None
    assert extracted["case_id"] == "SS-0001"

def test_extract_json_with_thinking_tags():
    """Verify Qwen3 thinking tags are stripped before parsing."""
    raw = f"<think>\nNeed to think about whether this is SSI or Trade Detail.\nIt is SSI.\n</think>\n{json.dumps(SAMPLE_VALID_REPORT)}"
    extracted = extract_json_from_llm_response(raw)
    assert extracted is not None
    assert extracted["candidate_failure_category"] == "SSI_MISMATCH"

