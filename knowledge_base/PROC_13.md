# Procedure PROC_13: General Settlement Exception Triage and Information Gathering

- **Procedure ID:** PROC_13
- **Title:** General Settlement Exception Triage and Information Gathering
- **Relevant Category:** UNDETERMINED
- **Source Type:** Synthetic / Illustrative Operational Guidance

## Trigger Indicators
- Settlement exception notification received with unspecified, truncated, or generic failure reason.
- System error message reports "Unknown Settlement Error" or "Manual Review Required".
- Narrative lacks critical trade parameters such as ISIN, currency, counterparty account, or transaction amount.

## Evidence to Inspect
- Original order management system (OMS) execution log and trade allocation history.
- Upstream and downstream gateway audit logs across messaging bridges.
- SWIFT MT548 settlement status notification messages and qualifier error codes.

## Generic Verification Steps
1. Perform comprehensive triage to extract all available settlement attributes (Trade ID, Counterparty, ISIN, Quantity, Amount, Settlement Date).
2. Check for missing mandatory fields required for categorization.
3. Review whether error code qualifies as a known technical transmission error vs operational trade discrepancy.
4. Retrieve the full raw MT548/status advice message from the custodian to identify specific sub-field status codes.
5. Cross-reference the trade ID against cancelled, amended, or duplicate bookings in the core ledger.

## Missing Information to Collect
- Full un-truncated custodian status notification and error detail code.
- Source trade execution ticket and confirmation recap from trading desk.

## Conditions for Human Escalation
- Essential transactional facts cannot be determined from available internal logs.
- Multiple conflicting indicators prevent definitive root-cause classification.

