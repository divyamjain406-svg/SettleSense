"""
RAG and Generation Pipeline for SettleSense.
Implements:
- Approach C: Prompt-only local LLM without retrieved context
- Approach D: Semantic retrieval + RAG with grounded context and citation validation
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import time
from typing import Dict, Any, List, Optional
from config.settings import CANONICAL_CATEGORIES, AMBIGUOUS_LABEL
from src.ollama_client import OllamaClient, OllamaServiceError
from src.semantic_retrieval import SemanticRetriever
from src.output_schemas import SettlementInvestigationReport
from src.output_validation import validate_report, ValidationResult

SYSTEM_INSTRUCTION = "You are SettleSense, an offline AI assistant for investigating securities settlement exceptions. Think briefly in under 40 words, then output valid JSON immediately."


def build_prompt_only_prompt(
    case_description: str,
    case_id: str = "CASE-TEMP",
    trade_type: str = "UNKNOWN",
    transaction_status: str = "UNKNOWN",
    exception_code: str = "UNKNOWN",
    classifier_hint: Optional[str] = None,
) -> str:
    """Constructs prompt for Approach C (Prompt-Only LLM)."""
    hint_block = f"\n- Optional Classifier Triage Hint: A baseline NLP classifier suggested candidate category '{classifier_hint}'. You may evaluate this suggestion, but make your final determination based on the evidence.\n" if classifier_hint else ""
    return f"""Investigate this settlement exception based ONLY on the provided case facts.

CASE INFORMATION:
- Case ID: {case_id}
- Trade Type: {trade_type}
- Status: {transaction_status}
- Exception Code: {exception_code}{hint_block}
- Exception Narrative: {case_description}

CATEGORIES (Allowed Categories: select the candidate category best supported by facts):
- SSI_MISMATCH: Standing instruction, safekeeping account, or depository agent mismatch.
- TRADE_DETAIL_MISMATCH: Price, quantity, currency, or settlement date discrepancy.
- SECURITIES_SHORTFALL: Custody inventory, borrow availability, or share shortfall.
- CASH_SHORTFALL: Nostro account, currency consideration, or cash deficit.
- COUNTERPARTY_UNCONFIRMED: Counterparty unconfirmed trade, affirmation, or allocation mismatch.
- SETTLEMENT_TIMING: Market cutoff passed, late batch release, or clearing window missed.
- UNDETERMINED: Case narrative is ambiguous, contradictory, uninformative, or truncated without distinguishing facts (e.g. unknown reason, generic error code, blank accounts, or conflicting logs).

Note: Select a specific category when the narrative provides concrete observed facts. Select UNDETERMINED if facts are incomplete, contradictory, or truncated.

Respond with valid JSON:
{{
  "case_id": "{case_id}",
  "case_summary": "Concise 1-sentence summary",
  "candidate_failure_category": "CATEGORY_NAME",
  "category_confidence_or_uncertainty": "HIGH | MEDIUM | LOW",
  "supporting_evidence": ["1-2 observed facts from narrative"],
  "possible_causes": ["1-2 plausible operational explanations"],
  "recommended_checks": ["1-2 verification checks"],
  "missing_information": ["Information to collect or None"],
  "procedure_references": [],
  "investigation_note": "Concise operational note",
  "requires_human_review": true
}}"""


def build_rag_prompt(
    case_description: str,
    retrieved_procedures: List[Dict[str, Any]],
    case_id: str = "CASE-TEMP",
    trade_type: str = "UNKNOWN",
    transaction_status: str = "UNKNOWN",
    exception_code: str = "UNKNOWN",
    classifier_hint: Optional[str] = None,
) -> str:
    """Constructs prompt for Approach D (Semantic Retrieval + Grounded RAG)."""
    p_summary = []
    proc_ids = []
    for proc in retrieved_procedures:
        pid = proc.get("procedure_id", "UNKNOWN")
        title = proc.get("title", "")
        raw_text = proc.get("passage_text", "")
        # Extract concise core excerpt (up to 200 chars) to prevent token bloat
        excerpt = raw_text[:200].strip().replace("\n", " ")
        proc_ids.append(pid)
        p_summary.append(f"- [{pid}] {title}: {excerpt}...")

    joined_evidence = "\n".join(p_summary) if p_summary else "No relevant procedures retrieved."
    hint_block = f"\n- Optional Classifier Triage Hint: A baseline NLP classifier suggested candidate category '{classifier_hint}'. You may evaluate this suggestion, but make your final determination based on the evidence.\n" if classifier_hint else ""

    example_pid = proc_ids[0] if proc_ids else "PROC_01"

    return f"""Investigate this settlement exception using the case facts and retrieved procedures:

CASE INFORMATION:
- Case ID: {case_id}
- Trade Type: {trade_type}
- Status: {transaction_status}
- Exception Code: {exception_code}{hint_block}
- Narrative: {case_description}

RETRIEVED PROCEDURE EVIDENCE:
{joined_evidence}

CATEGORIES (Allowed Categories: select the candidate category best supported by facts):
- SSI_MISMATCH: Discrepancy in depository safekeeping accounts, agent accounts, or standing settlement instructions.
- TRADE_DETAIL_MISMATCH: Discrepancy in trade economic terms (price, quantity, currency, settlement date).
- SECURITIES_SHORTFALL: Insufficient shares, borrow failure, or inventory deficit.
- CASH_SHORTFALL: Insufficient cash funds, Nostro deficit, or overdraft.
- COUNTERPARTY_UNCONFIRMED: Trade unconfirmed, counterparty unmatched, or missing affirmation.
- SETTLEMENT_TIMING: Market cutoff deadline passed, late batch release, or missed processing window.
- UNDETERMINED: Case narrative is ambiguous, contradictory, uninformative, or truncated without distinguishing facts (e.g. unknown reason, generic error code, blank accounts, or conflicting logs).

Note: Select a specific category when the narrative provides concrete observed facts. Select UNDETERMINED if facts are incomplete, contradictory, or truncated.
In 'procedure_references', cite ONLY procedure IDs that appear in the retrieved procedures above (allowed: {proc_ids}).

Respond with valid JSON:
{{
  "case_id": "{case_id}",
  "case_summary": "1-sentence summary",
  "candidate_failure_category": "CATEGORY_NAME",
  "category_confidence_or_uncertainty": "HIGH | MEDIUM | LOW",
  "supporting_evidence": ["1-2 key observed facts from narrative"],
  "possible_causes": ["1-2 plausible operational explanations"],
  "recommended_checks": ["1-2 verification checks citing {example_pid}"],
  "missing_information": ["Information to collect or None"],
  "procedure_references": ["{example_pid}"],
  "investigation_note": "Concise operational note",
  "requires_human_review": true
}}"""


class SettleSenseRAGPipeline:
    """End-to-End Investigation Copilot Pipeline."""

    def __init__(
        self,
        ollama_client: Optional[OllamaClient] = None,
        semantic_retriever: Optional[SemanticRetriever] = None,
    ):
        self.ollama_client = ollama_client or OllamaClient()
        self.semantic_retriever = semantic_retriever or SemanticRetriever(ollama_client=self.ollama_client)

    def run_prompt_only(
        self,
        case_description: str,
        case_id: str = "CASE-PROMPT",
        trade_type: str = "UNKNOWN",
        transaction_status: str = "UNKNOWN",
        exception_code: str = "UNKNOWN",
        classifier_hint: Optional[str] = None,
        timeout: Optional[Union[int, float]] = None,
    ) -> Dict[str, Any]:
        """
        Executes Approach C: Zero-shot Prompt-Only LLM without retrieval.
        """
        t0 = time.perf_counter()
        prompt = build_prompt_only_prompt(
            case_description=case_description,
            case_id=case_id,
            trade_type=trade_type,
            transaction_status=transaction_status,
            exception_code=exception_code,
            classifier_hint=classifier_hint,
        )

        try:
            t_llm = time.perf_counter()
            gen_resp = self.ollama_client.generate(
                prompt=prompt,
                system=SYSTEM_INSTRUCTION,
                format_type="json",
                timeout=timeout,
            )
            llm_s = round(time.perf_counter() - t_llm, 3)
            raw_text = gen_resp.get("response", "")
            val_result = validate_report(raw_text, case_description=case_description)
            latency = time.perf_counter() - t0

            gen_status = "SUCCESS" if (val_result.is_valid and val_result.report) else "INVALID_OUTPUT"

            return {
                "approach": "Approach C: Prompt-Only LLM",
                "case_id": case_id,
                "report": val_result.report,
                "validation": val_result,
                "raw_response": raw_text,
                "retrieved_procedures": [],
                "latency_seconds": round(latency, 3),
                "llm_latency_s": llm_s,
                "retrieval_latency_ms": 0.0,
                "success": val_result.is_valid,
                "generation_status": gen_status,
                "is_fallback": False,
                "error": None if val_result.is_valid else "; ".join(val_result.validation_errors),
            }

        except Exception as e:
            latency = time.perf_counter() - t0
            return self._build_error_fallback(case_id, str(e), latency, "Approach C: Prompt-Only LLM")

    def run_rag(
        self,
        case_description: str,
        case_id: str = "CASE-RAG",
        trade_type: str = "UNKNOWN",
        transaction_status: str = "UNKNOWN",
        exception_code: str = "UNKNOWN",
        classifier_hint: Optional[str] = None,
        top_k: int = 3,
        timeout: Optional[Union[int, float]] = None,
    ) -> Dict[str, Any]:
        """
        Executes Approach D: Semantic Retrieval + Grounded RAG with Citation Validation.
        """
        t0 = time.perf_counter()

        # 1. Semantic Retrieval
        retrieved_procedures = []
        ret_ms = 0.0
        try:
            if self.semantic_retriever.is_ready:
                t_ret = time.perf_counter()
                retrieved_procedures = self.semantic_retriever.retrieve(case_description, top_k=top_k)
                ret_ms = round((time.perf_counter() - t_ret) * 1000, 2)
        except Exception as e:
            print(f"Warning: Semantic retrieval failed ({e}); falling back to ungrounded generation.")

        # 2. Build Grounded Prompt
        prompt = build_rag_prompt(
            case_description=case_description,
            retrieved_procedures=retrieved_procedures,
            case_id=case_id,
            trade_type=trade_type,
            transaction_status=transaction_status,
            exception_code=exception_code,
            classifier_hint=classifier_hint,
        )

        # 3. Call Local LLM
        try:
            t_llm = time.perf_counter()
            gen_resp = self.ollama_client.generate(
                prompt=prompt,
                system=SYSTEM_INSTRUCTION,
                format_type="json",
                timeout=timeout,
            )
            llm_s = round(time.perf_counter() - t_llm, 3)
            raw_text = gen_resp.get("response", "")

            # 4. Validate output schema, citations, and evidence support
            val_result = validate_report(
                raw_text,
                case_description=case_description,
                retrieved_procedures=retrieved_procedures
            )
            latency = time.perf_counter() - t0

            gen_status = "SUCCESS" if (val_result.is_valid and val_result.report) else "INVALID_OUTPUT"

            return {
                "approach": "Approach D: Semantic RAG",
                "case_id": case_id,
                "report": val_result.report,
                "validation": val_result,
                "raw_response": raw_text,
                "retrieved_procedures": retrieved_procedures,
                "latency_seconds": round(latency, 3),
                "llm_latency_s": llm_s,
                "retrieval_latency_ms": ret_ms,
                "success": val_result.is_valid,
                "generation_status": gen_status,
                "is_fallback": False,
                "error": None if val_result.is_valid else "; ".join(val_result.validation_errors),
            }

        except Exception as e:
            latency = time.perf_counter() - t0
            return self._build_error_fallback(
                case_id, str(e), latency, "Approach D: Semantic RAG", retrieved_procedures
            )

    def _build_error_fallback(
        self,
        case_id: str,
        error_msg: str,
        latency: float,
        approach: str,
        retrieved_procedures: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Builds a safe, human-review-escalated fallback report when LLM is unavailable or errors."""
        err_lower = error_msg.lower()
        if "timed out" in err_lower or "timeout" in err_lower or "deadline" in err_lower:
            gen_status = "TIMEOUT_FALLBACK"
        elif "not found" in err_lower or "connection refused" in err_lower or "could not connect" in err_lower:
            gen_status = "MODEL_UNAVAILABLE"
        else:
            gen_status = "ERROR_FALLBACK"

        fallback_report = SettlementInvestigationReport(
            case_id=case_id,
            case_summary=f"Automated investigation failed due to local service issue: {error_msg}",
            candidate_failure_category="UNDETERMINED",
            category_confidence_or_uncertainty="UNCERTAIN",
            supporting_evidence=["System error prevented LLM completion."],
            possible_causes=["Local Ollama service offline or model response timeout."],
            recommended_checks=["Verify local Ollama service status and re-run investigation."],
            missing_information=["Full automated analysis output."],
            procedure_references=[],
            investigation_note="Automated copilot report could not be generated. Mandatory manual escalation required.",
            requires_human_review=True,
        )
        val_result = ValidationResult(
            is_valid=False,
            report=fallback_report,
            validation_errors=[error_msg],
            evidence_support_rate=0.0,
            is_fallback=True,
        )
        return {
            "approach": approach,
            "case_id": case_id,
            "report": fallback_report,
            "validation": val_result,
            "raw_response": "",
            "retrieved_procedures": retrieved_procedures or [],
            "latency_seconds": round(latency, 3),
            "llm_latency_s": round(latency, 3),
            "retrieval_latency_ms": 0.0,
            "success": False,
            "generation_status": gen_status,
            "is_fallback": True,
            "error": error_msg,
        }

