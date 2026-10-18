# Procedure PROC_08: Review Currency Funding Cutoffs and FX Settlement Timing

- **Procedure ID:** PROC_08
- **Title:** Review Currency Funding Cutoffs and FX Settlement Timing
- **Relevant Category:** CASH_SHORTFALL
- **Source Type:** Synthetic / Illustrative Operational Guidance

## Trigger Indicators
- Currency conversion or cross-currency funding leg failed to settle prior to security settlement window.
- Local currency clearing system cutoff time elapsed before funding reached agent bank.
- High-value cross-border payment held for compliance/AML review at correspondent bank.

## Evidence to Inspect
- Associated FX trade ticket and confirmation of currency conversion.
- SWIFT MT103/MT202 payment tracking message and payment system UETR status.
- Clearing house operating schedule and currency-specific cutoff timetable.

## Generic Verification Steps
1. Trace the funding flow from initial currency purchase to delivery into the settlement Nostro.
2. Cross-reference the payment release timestamp against the currency payment system cutoff time (e.g., CLS, Fedwire, TARGET2).
3. Confirm if the payment is held at an intermediary correspondent bank for Sanctions/AML screening.
4. Assess whether swap or rollover funding is required for overnight shortfall.
5. Notify counterparty settlement desk regarding projected receipt time of funds.

## Missing Information to Collect
- Payment tracking status (SWIFT GPI tracking reference) from correspondent bank.
- FX trading desk confirmation of completed swap/conversion leg.

## Conditions for Human Escalation
- Correspondent bank confirms funds blocked or rejected.
- Currency market has closed, causing unavoidable settlement fail to next business day.

