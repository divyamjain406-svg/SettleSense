# Procedure PROC_07: Verify Reported Cash Availability and Nostro Balances

- **Procedure ID:** PROC_07
- **Title:** Verify Reported Cash Availability and Nostro Balances
- **Relevant Category:** CASH_SHORTFALL
- **Source Type:** Synthetic / Illustrative Operational Guidance

## Trigger Indicators
- Settlement engine message: "Lack of Cash" or "Insufficient Funds at Cash Clearing Agent".
- Treasury notification indicating Nostro account overdraft or cap breach.
- DvP trade rejected by central bank settlement mechanism (e.g., Target2, Fedwire, CHAPS).

## Evidence to Inspect
- Real-time Nostro cash balance statement (MT940/MT942 or intraday cash ledger).
- Scheduled outgoing settlement payments for the current business cycle.
- Intraday credit facility utilization and debit cap parameters.

## Generic Verification Steps
1. Retrieve the intraday cash balance on the settlement Nostro account for the target currency.
2. Sum all pending scheduled debits due in the current settlement batch.
3. Determine if available balance covers the net debit required for the transaction.
4. Verify if incoming cash wires or completed sales settlements have posted.
5. Inquire whether intraday overdraft caps or collateralized liquidity facilities can be allocated.

## Missing Information to Collect
- Treasury cash management confirmation regarding pending currency transfers.
- Settlement bank statement confirming time of credit for expected inbound wire.

## Conditions for Human Escalation
- Nostro account is in overdraft without approved intraday credit extension.
- Treasury confirms currency liquidity shortage preventing timely settlement.

