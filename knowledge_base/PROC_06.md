# Procedure PROC_06: Investigate Pending Inbound Securities Transfers and Borrow Allocation

- **Procedure ID:** PROC_06
- **Title:** Investigate Pending Inbound Securities Transfers and Borrow Allocation
- **Relevant Category:** SECURITIES_SHORTFALL
- **Source Type:** Synthetic / Illustrative Operational Guidance

## Trigger Indicators
- Outbound delivery failing while corresponding inbound purchase trade remains unexecuted or unsettled.
- Securities lending borrow request pending confirmation from lending agent.
- Inbound conversion or depository depository-receipt issuance in progress.

## Evidence to Inspect
- Linked trade dependency chain and settlement queue status.
- Securities lending allocation report and borrow contract identifiers.
- Depository transfer status for upstream delivery legs.

## Generic Verification Steps
1. Trace upstream settlement references linked to the outbound delivery requirement.
2. Inquire with the delivering counterparty regarding the status of the upstream purchase.
3. Check the securities lending borrowing desk to confirm if a formal borrow ticket has been placed.
4. Verify if borrow settlement instructions were sent to the custodian with appropriate priority.
5. Coordinate with clearing operations to determine if partial delivery is permitted under market rules.

## Missing Information to Collect
- Delivering broker confirmation and CSD tracking reference for upstream inbound delivery.
- Approved securities lending borrow contract and delivery timeline.

## Conditions for Human Escalation
- Upstream delivering counterparty fails to provide an estimated time of delivery.
- Stock borrow fails to locate securities before market settlement cutoff.

