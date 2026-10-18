# Procedure PROC_09: Investigate Missing Counterparty Confirmation and Unmatched Instructions

- **Procedure ID:** PROC_09
- **Title:** Investigate Missing Counterparty Confirmation and Unmatched Instructions
- **Relevant Category:** COUNTERPARTY_UNCONFIRMED
- **Source Type:** Synthetic / Illustrative Operational Guidance

## Trigger Indicators
- Trade remains in "Awaiting Counterparty Confirmation" or "Unmatched" state beyond market matching deadline.
- Central matching utility (e.g., Traiana, Omgeo CTM, DTCC) reports zero incoming matching allegements.
- Counterparty operations desk has not acknowledged trade advice.

## Evidence to Inspect
- Outgoing confirmation transmission logs and electronic acknowledgement receipts.
- Counterparty contact directory, broker representative, and authorized escalation email list.
- Central matching engine queue status and counterparty participant ID.

## Generic Verification Steps
1. Verify that the outgoing confirmation was successfully dispatched to the correct counterparty BIC and queue.
2. Check whether counterparty traded under an executing broker model or prime broker give-up arrangement.
3. Determine whether the counterparty confirmed under an alternative entity identifier or LEI.
4. Issue an urgent electronic chaser or telephone inquiry to counterparty trade support.
5. Inquire whether the trade was cancelled or re-booked under an alternate internal ticket number.

## Missing Information to Collect
- Counterparty trade capture reference number and allocated trading desk contact.
- Confirmation of counterpart clearing broker or custodian appointment.

## Conditions for Human Escalation
- Counterparty explicitly denies knowledge of the executed trade.
- No response received within 4 hours of settlement matching cutoff.

