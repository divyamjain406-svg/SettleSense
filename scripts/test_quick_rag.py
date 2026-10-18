import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.rag_pipeline import SettleSenseRAGPipeline

pipeline = SettleSenseRAGPipeline()
res = pipeline.run_rag(
    case_description="Depository notification from Euroclear Brussels reported settlement failure for trade TRD-84920 with Northstar Brokerage. Internal safekeeping account SAFEKEEP-1021 does not match counterparty standing instructions specifying DEP-20412.",
    case_id="FOCUSED-INF-01",
    trade_type="EQUITY_BUY",
    transaction_status="SUSPENDED_DEP",
    exception_code="EXC_DEP_401",
)
print("SUCCESS:", res["success"])
print("STATUS:", res["generation_status"])
print("LATENCY:", res["latency_seconds"], "s (Ret:", res["retrieval_latency_ms"], "ms | LLM:", res["llm_latency_s"], "s)")
if res["report"]:
    print("CATEGORY:", res["report"].candidate_failure_category)
    print("CONFIDENCE:", res["report"].category_confidence_or_uncertainty)
    print("CITATIONS:", res["report"].procedure_references)
    print("HUMAN REVIEW:", res["report"].requires_human_review)
    print("EVIDENCE:", res["report"].supporting_evidence)
    print("CAUSES:", res["report"].possible_causes)
    print("EVIDENCE SUPPORT:", res["validation"].evidence_support_rate)
    print("CITATION VALIDITY:", res["validation"].citation_validity_rate)
else:
    print("ERROR:", res["error"])
    print("RAW:", repr(res["raw_response"]))

