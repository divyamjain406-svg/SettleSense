# SettleSense Synthetic Dataset Card

## 1. Dataset Summary
- **Dataset Name:** SettleSense Synthetic Settlement Exception Dataset
- **Version:** 1.0.0
- **Seed:** 42 (Fully deterministic)
- **Total Cases:** 240
  - **Labelled Exception Cases:** 210 (35 examples per canonical failure category across 6 categories)
  - **Ambiguous / Insufficient Cases:** 30 (`UNDETERMINED` label, `is_sufficiently_informative = False`)
- **Number of Scenario Families:** 48 families (7 families per canonical class + 6 ambiguous families)

## 2. Taxonomy & Class Breakdown

| Category Label | Description / Focus | Case Count |
|---|---|---|
| `SSI_MISMATCH` | Inconsistent safekeeping accounts, invalid clearing agent BICs, legacy SSI versioning, omnibus routing discrepancies. | 35 |
| `TRADE_DETAIL_MISMATCH` | Nominal quantity variances, currency conflicts, price/consideration disagreement, share class/ISIN mismatches. | 35 |
| `SECURITIES_SHORTFALL` | Unencumbered inventory deficit, corporate action escrow lockups, failed upstream purchases, stock borrow delays. | 35 |
| `CASH_SHORTFALL` | Intraday Nostro overdraft, credit cap limits, currency wire delays, FX funding cutoffs. | 35 |
| `COUNTERPARTY_UNCONFIRMED` | Unmatched utility queues, missing affirmations, counterparty blotter omission, prime broker give-up disputes. | 35 |
| `SETTLEMENT_TIMING` | Intended settlement date conflicts (T+1 vs T+2), local holiday closures, late depository batch release. | 35 |
| `UNDETERMINED` | Truncated status messages, missing mandatory fields, conflicting alerts without attribution. | 30 |

## 3. Schema Description

| Column | Type | Description |
|---|---|---|
| `case_id` | String | Unique synthetic identifier (e.g. `SS-0001`). Never encodes the target class. |
| `scenario_family_id` | String | Scenario grouping key (e.g. `FAM-SSI-01`) preventing near-paraphrase leakage during train/test splits. |
| `case_description` | String | Free-text operational exception narrative provided by analyst or custodian feed. |
| `trade_type` | String | Settlement contract type (e.g. `EQUITY_DVP`, `GOVT_BOND_DVP`, `REPO_CLOSING`). |
| `transaction_status` | String | Current transaction processing state (e.g. `REJECTED_CSD`, `UNMATCHED_MATCHING_UTILITY`). |
| `exception_code` | String | Synthetic error identifier code (e.g. `EXC_SSI_412`). |
| `expected_category` | String | Ground-truth failure category label (Evaluation only). |
| `ground_truth_evidence` | String | Key fact indicating the underlying exception cause (Evaluation only). |
| `relevant_procedure_ids` | String | Pipe-delimited IDs of knowledge base procedures addressing the exception (e.g. `PROC_01\|PROC_02`). |
| `is_sufficiently_informative` | Boolean | `True` for canonical cases; `False` for ambiguous cases. |

## 4. Evaluation and Privacy Guardrails
- **No Target Leakage:** Category names do not appear verbatim in descriptions or identifiers.
- **Group-Aware Splitting:** Train/test splits must stratify by scenario family so related variants remain strictly segregated.
- **Purely Synthetic:** Zero real customer, institution, or bank data.

