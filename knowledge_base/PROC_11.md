# Procedure PROC_11: Check Settlement Date and Market Processing Calendar

- **Procedure ID:** PROC_11
- **Title:** Check Settlement Date and Market Processing Calendar
- **Relevant Category:** SETTLEMENT_TIMING
- **Source Type:** Synthetic / Illustrative Operational Guidance

## Trigger Indicators
- Trade fails with "Invalid Settlement Date" or "Non-Business Day Settlement Requested".
- Discrepancy between contractual settlement cycle (e.g., T+1 vs T+2) across international jurisdictions.
- Regional bank holiday or market holiday closure affecting settlement currency or local CSD.

## Evidence to Inspect
- Market operating calendar for the target central securities depository and currency clearing system.
- Trade confirmation noting execution date (Trade Date) and intended settlement date (Value Date).
- Relevant market standard settlement cycle documentation (e.g., US T+1 rules vs European or Asian T+2 cycles).

## Generic Verification Steps
1. Verify the agreed settlement cycle (T+1, T+2, or extended settlement).
2. Check whether the designated settlement date falls on a weekend, local bank holiday, or national exchange closure.
3. Review currency clearing calendars if cross-currency settlement is involved.
4. Compare internal settlement date against counterparty instructed settlement date.
5. Inquire whether an amendment to the next mutual business day is required.

## Missing Information to Collect
- Depository holiday processing schedule notice.
- Agreed value date specification from original trade execution ticket.

## Conditions for Human Escalation
- Counterparty rejects proposed holiday date roll or claims penalty accrual.
- Settlement cycle dispute impacts derivative hedging or financing commitments.

