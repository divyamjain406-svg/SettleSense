# Procedure PROC_02: Review SSI Version and Effective Date Discrepancies

- **Procedure ID:** PROC_02
- **Title:** Review SSI Version and Effective Date Discrepancies
- **Relevant Category:** SSI_MISMATCH
- **Source Type:** Synthetic / Illustrative Operational Guidance

## Trigger Indicators
- Trade fails with "De-activated SSI" or "Expired Standing Instruction" notice from custodian or clearing house.
- Recent SSI update notice received near trade execution date.
- Counterparty used an older instruction version while internal records utilized an updated release.

## Evidence to Inspect
- SSI audit log indicating timestamp and effective dates of instruction changes.
- Trade execution timestamp versus SSI activation timestamp.
- Counterparty notification letter or authenticated broadcast advising instruction transition.

## Generic Verification Steps
1. Retrieve the effective commencement date of the current SSI record in the repository.
2. Determine whether the trade trade-date preceded or succeeded the SSI effective changeover date.
3. Establish whether market transition rules mandate settlement under legacy instructions for trades agreed prior to the cutoff date.
4. Compare version numbers between the internal settlement engine and counterparty instruction message.
5. Identify whether pending cancels and re-issues are required at the central securities depository (CSD).

## Missing Information to Collect
- Depository transition notice confirming grandfathering rules for existing open trades.
- Formal counterparty acknowledgement of the revised instruction profile.

## Conditions for Human Escalation
- Counterparty refutes the activation timestamp of the revised instruction.
- The custodian has blocked automated cancellation and repair pending compliance sign-off.

