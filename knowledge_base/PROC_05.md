# Procedure PROC_05: Review Reported Securities Availability and Custodian Position

- **Procedure ID:** PROC_05
- **Title:** Review Reported Securities Availability and Custodian Position
- **Relevant Category:** SECURITIES_SHORTFALL
- **Source Type:** Synthetic / Illustrative Operational Guidance

## Trigger Indicators
- Custodian status notification: "Settlement pending: Lack of securities" or "Insufficient position".
- Depository instruction recycling due to inadequate unencumbered inventory.
- Settlement failure penalty warnings triggered under CSDR or local settlement discipline regime.

## Evidence to Inspect
- Real-time custodian safekeeping position statement (MT535).
- Internal ledger position and pending settlement queues.
- Segregated, pledged, or encumbered collateral balances.

## Generic Verification Steps
1. Retrieve current available and unencumbered quantity for the target ISIN at the relevant depository.
2. Deduct all prior-priority pending outbound deliveries from total settled inventory.
3. Determine whether any portion of the balance is restricted due to corporate action escrow, repo lien, or collateral pledge.
4. Verify if incoming trades from earlier settlement batches are pending settlement to replenish inventory.
5. Inquire whether inventory exists at an alternate depository and requires free-of-payment inter-depository realignment.

## Missing Information to Collect
- Real-time statement from custodian confirming actual unsettled versus free settled balance.
- Internal stock loan desk confirmation regarding borrowing status.

## Conditions for Human Escalation
- Deficit cannot be resolved prior to the final market recycling cutoff.
- Potential CSDR settlement fail penalties or buy-in procedures are imminent.

