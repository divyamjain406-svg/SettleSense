# Procedure PROC_10: Review Counterparty Matching Discrepancies and Unresolved Allegations

- **Procedure ID:** PROC_10
- **Title:** Review Counterparty Matching Discrepancies and Unresolved Allegations
- **Relevant Category:** COUNTERPARTY_UNCONFIRMED
- **Source Type:** Synthetic / Illustrative Operational Guidance

## Trigger Indicators
- Counterparty alleges a transaction with conflicting trade terms, direction (buy vs sell), or settlement mechanism (FOP vs DVP).
- Status reported as "Counterparty Discrepancy Flagged" or "Pending Dispute Resolution".
- Incoming allegement exists in central matching system but fails internal auto-match rules.

## Evidence to Inspect
- Central matching utility side-by-side comparison report.
- Front-office voice log or electronic chat confirmation (Bloomberg/Symphony/Tradeweb).
- Internal vs external trade direction (Receive vs Deliver, Buy vs Sell).

## Generic Verification Steps
1. Compare incoming allegement attributes against internal trade booking (Trade Date, Settlement Date, Direction, Consideration).
2. Confirm whether counterparty booked the transaction inverted (e.g., both sides booked as Buy).
3. Check whether trade was negotiated as Delivery-versus-Payment (DvP) but instructed as Free-of-Payment (FoP).
4. Review bilateral trade ticket exchange between respective middle-office operations teams.
5. Identify the exact mismatching field blocking automatic central matching.

## Missing Information to Collect
- Front-office deal audit transcript confirming negotiated transaction terms.
- Counterparty operational representative reconciliation breakdown.

## Conditions for Human Escalation
- Contradictory transaction direction or fundamental deal economic dispute.
- Counterparty alleges a trade for which no internal front-office booking exists.

