import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
from src.ollama_client import OllamaClient
from src.semantic_retrieval import SemanticRetriever

client = OllamaClient()
retriever = SemanticRetriever()
procs = retriever.retrieve("Depository notification from Euroclear Brussels reported settlement failure for trade TRD-84920 with Northstar Brokerage. Internal safekeeping account SAFEKEEP-1021 does not match counterparty standing instructions specifying DEP-20412.", top_k=2)

p_summary = []
for p in procs:
    pid = p["procedure_id"]
    title = p["title"]
    text = p["passage_text"][:180].strip()
    p_summary.append(f"- [{pid}] {title}: {text}...")
proc_text = "\n".join(p_summary)

prompt = f"""Investigate this settlement exception using the case facts and retrieved procedures:

CASE INFORMATION:
- Case ID: SS-0001
- Trade Type: EQUITY_BUY
- Status: SUSPENDED_DEP
- Exception Code: EXC_DEP_401
- Narrative: Depository notification from Euroclear Brussels reported settlement failure for trade TRD-84920 with Northstar Brokerage. Internal safekeeping account SAFEKEEP-1021 does not match counterparty standing instructions specifying DEP-20412.

RETRIEVED PROCEDURES:
{proc_text}

CATEGORIES (Select the best candidate category supported by facts):
- SSI_MISMATCH: Discrepancy in depository safekeeping accounts or standing instructions.
- TRADE_DETAIL_MISMATCH: Discrepancy in price, quantity, currency, or settlement date.
- SECURITIES_SHORTFALL: Insufficient shares or borrow failure.
- CASH_SHORTFALL: Insufficient funds or Nostro deficit.
- COUNTERPARTY_UNCONFIRMED: Trade unconfirmed or counterparty unmatched.
- SETTLEMENT_TIMING: Depository cutoff deadline exceeded.
- UNDETERMINED: Genuinely ambiguous or contradictory facts.

Output valid JSON:
{{
  "case_id": "SS-0001",
  "case_summary": "1-sentence summary",
  "candidate_failure_category": "SSI_MISMATCH",
  "category_confidence_or_uncertainty": "HIGH",
  "supporting_evidence": ["Safekeeping account SAFEKEEP-1021 does not match DEP-20412."],
  "possible_causes": ["Standing instructions outdated at depository."],
  "recommended_checks": ["Review master SSI profile using PROC_01."],
  "missing_information": ["None"],
  "procedure_references": ["PROC_01"],
  "investigation_note": "High probability of standing instruction error.",
  "requires_human_review": true
}}"""

system = "You are SettleSense. Think briefly in under 40 words, then output JSON immediately."

t0 = time.time()
res = client.generate(prompt=prompt, system=system)
print(f"Elapsed: {time.time()-t0:.2f}s")
print("THINKING LEN:", len(res.get("thinking", "")))
print("RESPONSE LEN:", len(res.get("response", "")))
print("DONE REASON:", res.get("raw", {}).get("done_reason"))
print("RESPONSE:", res.get("response", ""))

