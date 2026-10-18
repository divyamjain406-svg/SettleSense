"""
Output validation module for SettleSense.
Validates Pydantic structured output, verifies citation IDs against known knowledge base
procedures, detects hallucinated references, and extracts JSON from LLM responses.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import re
from typing import Dict, Any, List, Set, Tuple, Optional
from pydantic import ValidationError

from config.settings import KNOWLEDGE_BASE_DIR
from src.output_schemas import SettlementInvestigationReport


def get_known_procedure_ids(kb_dir: Path = KNOWLEDGE_BASE_DIR) -> Set[str]:
    """Retrieves all legitimate procedure IDs present in the knowledge base."""
    ids = set()
    for file_path in kb_dir.glob("PROC_*.md"):
        # Match PROC_01 through PROC_99
        match = re.search(r"PROC_\d+", file_path.stem)
        if match:
            ids.add(match.group(0))
        # Also parse content if stem differs
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            id_in_text = re.search(r"\*\*Procedure ID:\*\*\s*(PROC_\d+)", content)
            if id_in_text:
                ids.add(id_in_text.group(1))
    return ids


def extract_json_from_llm_response(raw_text: str) -> Optional[Dict[str, Any]]:
    """
    Robustly extracts JSON object from raw LLM output.
    Handles thinking tags (<think>...</think>), markdown code blocks (```json ... ```),
    or raw JSON strings.
    """
    if not isinstance(raw_text, str):
        return None

    cleaned = raw_text.strip()

    # Remove Qwen3 thinking block if present
    cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL).strip()

    # Match JSON block within markdown fences ```json ... ```
    md_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, flags=re.DOTALL)
    if md_match:
        try:
            return json.loads(md_match.group(1))
        except json.JSONDecodeError:
            pass

    # Match raw JSON object enclosed in braces { ... }
    brace_match = re.search(r"(\{.*\})", cleaned, flags=re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(1))
        except json.JSONDecodeError:
            pass

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


class ValidationResult:
    """Container for output report validation metrics."""

    def __init__(
        self,
        is_valid: bool,
        report: Optional[SettlementInvestigationReport] = None,
        raw_dict: Optional[Dict[str, Any]] = None,
        validation_errors: Optional[List[str]] = None,
        valid_citations: Optional[List[str]] = None,
        invalid_citations: Optional[List[str]] = None,
        citation_validity_rate: float = 1.0,
        evidence_support_rate: float = 1.0,
        unsupported_evidence: Optional[List[str]] = None,
        is_fallback: bool = False,
    ):
        self.is_valid = is_valid
        self.report = report
        self.raw_dict = raw_dict or {}
        self.validation_errors = validation_errors or []
        self.valid_citations = valid_citations or []
        self.invalid_citations = invalid_citations or []
        self.citation_validity_rate = citation_validity_rate
        self.evidence_support_rate = evidence_support_rate
        self.unsupported_evidence = unsupported_evidence or []
        self.is_fallback = is_fallback

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "has_report": self.report is not None,
            "validation_errors": self.validation_errors,
            "valid_citations": self.valid_citations,
            "invalid_citations": self.invalid_citations,
            "citation_validity_rate": self.citation_validity_rate,
            "evidence_support_rate": self.evidence_support_rate,
            "unsupported_evidence": self.unsupported_evidence,
            "is_fallback": self.is_fallback,
            "requires_human_review": self.report.requires_human_review if self.report else True,
        }


def verify_evidence_support(
    report: Union[SettlementInvestigationReport, List[str]],
    case_description: str,
    retrieved_procedures: Optional[List[Any]] = None,
) -> Tuple[float, List[str]]:
    """
    Automated Evidence-Validator Pass Rate (Heuristic Grounding Check):
    Algorithmically verifies that claims in supporting_evidence cite entities, numbers,
    and terminology present in the case narrative or retrieved procedure passages,
    preventing fabricated figures or phantom accounts.
    
    NOTE: This automated metric measures heuristic lexical/entity grounding consistency.
    It is distinct from human-reviewed operational evidence support, which requires a
    qualified settlement subject-matter expert (SME) to evaluate factual completeness.
    Returns (automated_evidence_pass_rate, list_of_unsupported_evidence).
    Fallback reports are excluded and assigned 0.0 support.
    """
    if hasattr(report, "case_summary") and "automated investigation failed" in str(report.case_summary).lower():
        return 0.0, ["Fallback report generated from service error; ungrounded."]

    if isinstance(report, list):
        evidence_statements = report
    elif hasattr(report, "supporting_evidence"):
        evidence_statements = report.supporting_evidence
    else:
        evidence_statements = []

    if not evidence_statements:
        return 1.0, []

    # Build reference context text
    context_text = case_description.lower()
    if retrieved_procedures:
        for p in retrieved_procedures:
            if isinstance(p, dict):
                context_text += " " + p.get("passage_text", "").lower()
            elif isinstance(p, str):
                context_text += " " + p.lower()

    unsupported = []
    supported_count = 0

    for ev_statement in evidence_statements:
        ev_lower = ev_statement.lower()
        # Extract potential specific entities: numbers, IDs (ISINs, TRD-), amounts
        specific_tokens = re.findall(r"\b(?:[A-Z0-9]{2,}[A-Z0-9_-]+|\d+(?:,\d{3})*(?:\.\d+)?)\b", ev_statement)

        # Check if substantive tokens exist in context
        if specific_tokens:
            unmatched_tokens = [tok for tok in specific_tokens if tok.lower() not in context_text and len(tok) > 2]
            if len(unmatched_tokens) > len(specific_tokens) // 2:
                unsupported.append(ev_statement)
                continue

        # If general statement, check if at least 2 substantive non-stopword terms overlap
        words = [w for w in re.findall(r"\b\w{4,}\b", ev_lower) if w not in {"that", "with", "from", "were", "been", "have", "this"}]
        matching_words = [w for w in words if w in context_text]
        if words and len(matching_words) == 0:
            unsupported.append(ev_statement)
        else:
            supported_count += 1

    total = len(evidence_statements)
    rate = supported_count / total if total > 0 else 1.0
    return round(rate, 4), unsupported


def validate_report(
    raw_response: Any,
    known_proc_ids: Optional[Set[str]] = None,
    case_description: Optional[str] = None,
    retrieved_procedures: Optional[List[Dict[str, Any]]] = None,
) -> ValidationResult:
    """
    Validates LLM response dictionary or JSON string against SettlementInvestigationReport schema,
    verifies procedure citations, and checks evidence grounding support rate.
    """
    if known_proc_ids is None:
        known_proc_ids = get_known_procedure_ids()

    # 1. Parse JSON
    if isinstance(raw_response, str):
        data = extract_json_from_llm_response(raw_response)
        if data is None:
            return ValidationResult(
                is_valid=False,
                validation_errors=["Failed to parse response as valid JSON format."]
            )
    elif isinstance(raw_response, dict):
        data = raw_response
    else:
        return ValidationResult(
            is_valid=False,
            validation_errors=[f"Unsupported input type for validation: {type(raw_response)}"]
        )

    # 2. Validate against Pydantic schema
    try:
        report = SettlementInvestigationReport(**data)
    except ValidationError as e:
        error_msgs = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
        return ValidationResult(
            is_valid=False,
            raw_dict=data,
            validation_errors=error_msgs
        )

    # 3. Validate procedure citations
    valid_cites = []
    invalid_cites = []

    for cite in report.procedure_references:
        # Standardize ID format (e.g. PROC_01)
        match = re.search(r"PROC_\d+", cite.upper())
        canonical_id = match.group(0) if match else cite.strip()
        if canonical_id in known_proc_ids:
            valid_cites.append(canonical_id)
        else:
            invalid_cites.append(cite)

    total_cites = len(report.procedure_references)
    if total_cites > 0:
        validity_rate = len(valid_cites) / total_cites
    else:
        # If no citations were made, validity rate is 1.0 (no hallucinations)
        validity_rate = 1.0

    validation_errors = []
    if invalid_cites:
        validation_errors.append(f"Nonexistent procedure IDs cited: {invalid_cites}")

    # 4. Evidence Support Rate
    evidence_support_rate = 1.0
    unsupported_ev = []
    if case_description:
        evidence_support_rate, unsupported_ev = verify_evidence_support(
            report, case_description, retrieved_procedures
        )

    is_valid_report = (len(invalid_cites) == 0)

    return ValidationResult(
        is_valid=is_valid_report,
        report=report,
        raw_dict=data,
        validation_errors=validation_errors,
        valid_citations=valid_cites,
        invalid_citations=invalid_cites,
        citation_validity_rate=validity_rate,
        evidence_support_rate=evidence_support_rate,
        unsupported_evidence=unsupported_ev,
    )

