# Procedure PROC_01: Verify Standard Settlement Instruction (SSI) Account Consistency

- **Procedure ID:** PROC_01
- **Title:** Verify Standard Settlement Instruction (SSI) Account Consistency
- **Relevant Category:** SSI_MISMATCH
- **Source Type:** Synthetic / Illustrative Operational Guidance

## Trigger Indicators
- Settlement instruction rejection citing invalid or mismatched depository account number.
- Counterparty trade notification indicates settlement venue or agent BIC differs from internal SSI database.
- Depository instruction status indicates "NACK: Invalid Safekeeping Account" or "Unrecognised Beneficiary".

## Evidence to Inspect
- Internal trade booking record and designated settlement agent/depository account.
- Counterparty MT541/MT543 or equivalent SWIFT settlement message.
- Global repository master SSI profile for counterparty and relevant market/currency.

## Generic Verification Steps
1. Extract the depository account number, safekeeping account, and settlement agent BIC from the internal booking.
2. Retrieve the counterparty's published standard settlement instruction in the golden-source SSI repository (e.g., ALERT or internal repository).
3. Compare the internal instruction against the counterparty's advised instruction field-by-field.
4. Verify whether an account override was manually keyed during trade capture.
5. Check if the sub-custodian account matches the counterparty's clearing agent for the specified security exchange.

## Missing Information to Collect
- Signed SSI amendment confirmation or authenticated standing instruction notice.
- Counterparty operational contact confirmation of intended settlement conduit.

## Conditions for Human Escalation
- Counterparty insists on an account that does not match authorized standing instructions on file.
- Discrepancy involves high-value transactions exceeding local operations desk authorization thresholds.

