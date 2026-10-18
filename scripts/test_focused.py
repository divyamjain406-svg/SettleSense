"""
Focused validation script to verify Approach C and Approach D on:
1. An informative SSI_MISMATCH case.
2. A genuinely ambiguous case.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
import json
from src.rag_pipeline import SettleSenseRAGPipeline

def run_focused_tests():
    pipeline = SettleSenseRAGPipeline()

    informative_desc = (
        "Depository notification from Euroclear Brussels reported settlement failure for trade TRD-84920 "
        "with Northstar Brokerage. Internal safekeeping account SAFEKEEP-1021 does not match counterparty "
        "standing instructions specifying DEP-20412."
    )

    ambiguous_desc = (
        "Settlement failure notification received from Clearstream Banking Luxembourg for trade AMB-001-3219 "
        "with Borealis Investment Banking. Status indicates 'FAIL - UNKNOWN REASON'. The message text is "
        "truncated and contains no error sub-codes, counterparty account details, or diagnostic information."
    )

    print("==================================================================")
    print(" FOCUSED TEST 1: INFORMATIVE CASE (Expected: SSI_MISMATCH)")
    print("==================================================================")

    # 1. Approach C: Prompt-Only
    print("\n--- Running Approach C (Prompt-Only) ---")
    res_c = pipeline.run_prompt_only(
        case_description=informative_desc,
        case_id="FOCUSED-INF-01",
        trade_type="EQUITY_BUY",
        transaction_status="SUSPENDED_DEP",
        exception_code="EXC_DEP_401",
    )
    print(f"Status: {res_c.get('generation_status')}")
    print(f"Latency: {res_c.get('latency_seconds')}s (LLM: {res_c.get('llm_latency_s')}s)")
    if res_c.get("report"):
        print(f"Predicted Category: {res_c['report'].candidate_failure_category}")
        print(f"Confidence: {res_c['report'].category_confidence_or_uncertainty}")
        print(f"Requires Human Review: {res_c['report'].requires_human_review}")
        print(f"Supporting Evidence: {res_c['report'].supporting_evidence}")
        print(f"Possible Causes: {res_c['report'].possible_causes}")

    # 2. Approach D: Semantic RAG
    print("\n--- Running Approach D (Semantic RAG) ---")
    res_d = pipeline.run_rag(
        case_description=informative_desc,
        case_id="FOCUSED-INF-01",
        trade_type="EQUITY_BUY",
        transaction_status="SUSPENDED_DEP",
        exception_code="EXC_DEP_401",
    )
    print(f"Status: {res_d.get('generation_status')}")
    print(f"Latency: {res_d.get('latency_seconds')}s (Ret: {res_d.get('retrieval_latency_ms')}ms | LLM: {res_d.get('llm_latency_s')}s)")
    print(f"Retrieved Procedures: {[p['procedure_id'] for p in res_d.get('retrieved_procedures', [])]}")
    if res_d.get("report"):
        print(f"Predicted Category: {res_d['report'].candidate_failure_category}")
        print(f"Confidence: {res_d['report'].category_confidence_or_uncertainty}")
        print(f"Citations: {res_d['report'].procedure_references}")
        print(f"Requires Human Review: {res_d['report'].requires_human_review}")
        print(f"Supporting Evidence: {res_d['report'].supporting_evidence}")
        print(f"Possible Causes: {res_d['report'].possible_causes}")
        print(f"Evidence Support Rate: {res_d['validation'].evidence_support_rate}")
        print(f"Citation Validity Rate: {res_d['validation'].citation_validity_rate}")

    print("\n==================================================================")
    print(" FOCUSED TEST 2: AMBIGUOUS CASE (Expected: UNDETERMINED)")
    print("==================================================================")

    # 3. Ambiguous Case - Approach D: Semantic RAG
    print("\n--- Running Approach D on Ambiguous Case ---")
    res_amb = pipeline.run_rag(
        case_description=ambiguous_desc,
        case_id="FOCUSED-AMB-01",
        trade_type="CROSS_BORDER_DVP",
        transaction_status="SUSPENDED_UNSPECIFIED",
        exception_code="EXC_AMB_106",
    )
    print(f"Status: {res_amb.get('generation_status')}")
    print(f"Latency: {res_amb.get('latency_seconds')}s (Ret: {res_amb.get('retrieval_latency_ms')}ms | LLM: {res_amb.get('llm_latency_s')}s)")
    print(f"Retrieved Procedures: {[p['procedure_id'] for p in res_amb.get('retrieved_procedures', [])]}")
    if res_amb.get("report"):
        print(f"Predicted Category: {res_amb['report'].candidate_failure_category}")
        print(f"Confidence: {res_amb['report'].category_confidence_or_uncertainty}")
        print(f"Citations: {res_amb['report'].procedure_references}")
        print(f"Missing Information: {res_amb['report'].missing_information}")
        print(f"Requires Human Review: {res_amb['report'].requires_human_review}")
        print(f"Evidence Support Rate: {res_amb['validation'].evidence_support_rate}")

if __name__ == "__main__":
    run_focused_tests()
