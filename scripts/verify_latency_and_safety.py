#!/usr/bin/env python3
"""
Verification script for:
1. Deliberately timed-out request interrupted within configured deadline.
2. Single informative RAG case returning supported category with valid citations.
3. Single ambiguous case returning UNDETERMINED with human review flag.
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.rag_pipeline import SettleSenseRAGPipeline
from src.ollama_client import OllamaTimeoutError

def main():
    pipeline = SettleSenseRAGPipeline()

    print("==================================================================")
    print(" 1. Testing Deliberate Hard Timeout Interruption (deadline=0.01s)")
    print("==================================================================")
    t0 = time.perf_counter()
    timeout_res = pipeline.run_rag(
        case_description="Delayed batch timing exception at clearing house.",
        case_id="VERIFY-TIMEOUT",
        timeout=0.01,
    )
    t_elapsed = time.perf_counter() - t0
    print(f"Elapsed Wall-Clock: {t_elapsed:.3f}s (pipeline recorded: {timeout_res['latency_seconds']:.3f}s)")
    print(f"Generation Status: {timeout_res['generation_status']}")
    print(f"Is Fallback: {timeout_res['is_fallback']}")
    print(f"Report Category: {timeout_res['report'].candidate_failure_category}")
    print(f"Requires Human Review: {timeout_res['report'].requires_human_review}")
    print(f"Evidence Support Rate: {timeout_res['validation'].evidence_support_rate}")
    
    assert timeout_res["generation_status"] == "TIMEOUT_FALLBACK", "Should be TIMEOUT_FALLBACK"
    assert timeout_res["is_fallback"] is True, "Should be fallback"
    assert timeout_res["report"].requires_human_review is True, "Must require human review"
    assert timeout_res["report"].candidate_failure_category == "UNDETERMINED", "Category must be UNDETERMINED"
    assert timeout_res["validation"].evidence_support_rate == 0.0, "Fallback cannot inflate evidence support"
    assert t_elapsed < 1.0, "Timeout must abort quickly"
    print(">>> PASS: Hard deadline interrupted within deadline and recorded accurately.\n")

    print("==================================================================")
    print(" 2. Testing Single Informative Case (Expected: SSI_MISMATCH)")
    print("==================================================================")
    t0 = time.perf_counter()
    info_res = pipeline.run_rag(
        case_description="Safekeeping account 99201 rejected by depository due to incorrect standing instruction profile.",
        case_id="VERIFY-SSI",
        trade_type="EQUITY_BUY",
        exception_code="ERR-SSI-01",
        timeout=120,
    )
    t_elapsed = time.perf_counter() - t0
    report = info_res["report"]
    val = info_res["validation"]
    print(f"Elapsed: {t_elapsed:.2f}s | Retrieval: {info_res['retrieval_latency_ms']:.1f}ms | LLM: {info_res['llm_latency_s']:.2f}s")
    print(f"Status: {info_res['generation_status']}")
    print(f"Predicted Category: {report.candidate_failure_category}")
    print(f"Citations: {report.procedure_references}")
    print(f"Citation Validity: {val.citation_validity_rate}")
    print(f"Evidence Support: {val.evidence_support_rate}")
    
    assert info_res["generation_status"] == "SUCCESS", "Informative case should succeed"
    assert report.candidate_failure_category == "SSI_MISMATCH", "Category should be SSI_MISMATCH"
    assert len(report.procedure_references) > 0, "Must cite procedures"
    assert val.citation_validity_rate == 1.0, "Citations must be valid"
    assert val.evidence_support_rate == 1.0, "Evidence must be supported"
    print(">>> PASS: Informative case succeeded with supported category and valid citations.\n")

    print("==================================================================")
    print(" 3. Testing Single Ambiguous Case (Expected: UNDETERMINED)")
    print("==================================================================")
    t0 = time.perf_counter()
    amb_res = pipeline.run_rag(
        case_description="Settlement failure notification received from Clearstream Banking Luxembourg for trade AMB-001-3219 with Borealis Investment Banking. Status indicates 'FAIL - UNKNOWN REASON'. The message text is truncated and contains no error sub-codes, counterparty account details, or diagnostic information.",
        case_id="VERIFY-AMB-SS-0211",
        trade_type="CROSS_BORDER_DVP",
        exception_code="EXC_AMB_106",
        timeout=120,
    )
    t_elapsed = time.perf_counter() - t0
    amb_report = amb_res["report"]
    amb_val = amb_res["validation"]
    print(f"Elapsed: {t_elapsed:.2f}s | Status: {amb_res['generation_status']}")
    print(f"Predicted Category: {amb_report.candidate_failure_category}")
    print(f"Confidence: {amb_report.category_confidence_or_uncertainty}")
    print(f"Requires Human Review: {amb_report.requires_human_review}")
    print(f"Missing Info: {amb_report.missing_information}")
    
    assert amb_res["generation_status"] == "SUCCESS", "Ambiguous case should complete successfully"
    assert amb_report.candidate_failure_category == "UNDETERMINED", "Category should be UNDETERMINED"
    assert amb_report.requires_human_review is True, "Ambiguous case MUST require human review"
    print(">>> PASS: Ambiguous case correctly predicted UNDETERMINED with mandatory human escalation.\n")

    print("All focused verification checks PASSED successfully!")

if __name__ == "__main__":
    main()

