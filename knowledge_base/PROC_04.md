# Procedure PROC_04: Verify Trade Currency, Price, and Net Settlement Amount

- **Procedure ID:** PROC_04
- **Title:** Verify Trade Currency, Price, and Net Settlement Amount
- **Relevant Category:** TRADE_DETAIL_MISMATCH
- **Source Type:** Synthetic / Illustrative Operational Guidance

## Trigger Indicators
- Matching failure citing net consideration or settlement cash amount discrepancy.
- Trade currency mismatch between trading currency and settlement settlement currency.
- Accrued interest or commission fee discrepancy exceeding market settlement tolerance.

## Evidence to Inspect
- Deal recap sheet or electronic order audit trail.
- Broker confirmation notice specifying gross price, clean price, dirty price, and commission breakdown.
- Market convention rules for day count and accrued interest calculations (especially for fixed income).

## Generic Verification Steps
1. Verify the agreed currency code (ISO 4217) across both records.
2. Calculate expected net cash amount: (Quantity * Price) +/- Accrued Interest +/- Commissions/Taxes.
3. Compare calculated net cash against both internal and counterparty advised amounts.
4. Assess whether the difference is within CSD automatic matching tolerance (e.g., standard small currency tolerance).
5. For bond transactions, cross-check settlement day-count conventions (e.g., 30/360 vs Actual/Actual).

## Missing Information to Collect
- Detailed fee schedule or broker trade recap detailing accrued interest and brokerage charges.
- Confirmation of agreed clean vs dirty price quoting conventions.

## Conditions for Human Escalation
- Price variance indicates execution disagreement between trading desks.
- Currency mismatch requires booking currency conversion adjustment outside operational delegation limits.

