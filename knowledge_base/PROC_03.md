# Procedure PROC_03: Compare Trade Quantity and Security Identifier

- **Procedure ID:** PROC_03
- **Title:** Compare Trade Quantity and Security Identifier
- **Relevant Category:** TRADE_DETAIL_MISMATCH
- **Source Type:** Synthetic / Illustrative Operational Guidance

## Trigger Indicators
- Central matching utility (e.g., CTM) generates quantity mismatch exception.
- Security identifier (ISIN, CUSIP, SEDOL) disagreement flagged by depository or counterparty.
- Partial fills reported with inconsistent unit denominations.

## Evidence to Inspect
- Front-office execution ticket, block allocation breakdown, and electronic confirmation.
- Counterparty incoming trade allocation notification.
- Security master reference data verifying ISIN, nominal value, and security ticker.

## Generic Verification Steps
1. Compare the ISIN, CUSIP, and SEDOL between internal booking and counterparty confirmation.
2. Confirm whether corporate actions (e.g., stock splits, reverse splits, or symbol changes) altered security identifiers or nominal shares.
3. Compare gross nominal quantity and share units. Check for common clerical unit errors (e.g., thousands vs units).
4. Review block allocation distributions across underlying client sub-accounts.
5. Identify whether a partial delivery occurred and whether the trade status reflects remaining open balance.

## Missing Information to Collect
- Front-office trading desk clarification regarding agreed lot size or amended terms.
- Counterparty allocation confirmation sheet.

## Conditions for Human Escalation
- Front-office trading desks dispute the agreed nominal quantity.
- The discrepancy suggests execution of an entirely different security series or class.

