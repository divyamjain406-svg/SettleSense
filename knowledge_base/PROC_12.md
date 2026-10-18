# Procedure PROC_12: Investigate Depository Cutoff Timing and Late Release Exceptions

- **Procedure ID:** PROC_12
- **Title:** Investigate Depository Cutoff Timing and Late Release Exceptions
- **Relevant Category:** SETTLEMENT_TIMING
- **Source Type:** Synthetic / Illustrative Operational Guidance

## Trigger Indicators
- Instruction rejected due to submission past market input deadline or batch cutoff window.
- Internal instruction held in pending release queue past real-time gross settlement cutoff.
- "Late Matching" or "Cutoff Exceeded" penalty warning from market infrastructure.

## Evidence to Inspect
- CSD/ICSD daily operating timetable and specific instruction cutoff timestamps (e.g., Euroclear, Clearstream, DTC).
- Internal settlement system dispatch timestamp and queue audit log.
- Time-stamped electronic transmission logs to the local sub-custodian or clearing agent.

## Generic Verification Steps
1. Determine the exact market cutoff time for matching, free delivery, and against-payment settlement.
2. Compare the instruction release timestamp against the applicable market input cutoff.
3. Identify whether internal operational bottlenecks, batch processing delays, or batch job latency caused late release.
4. Check whether late-night or same-day night batch processing windows are available.
5. Notify front-office trading desk and client service team of delayed settlement to the next cycle.

## Missing Information to Collect
- Custodian batch release audit trail confirming time of message delivery.
- Internal queue dispatch timestamp report.

## Conditions for Human Escalation
- Late instruction submission triggers mandatory buy-in or significant regulatory penalty.
- Systematic infrastructure batch processing failure impacting multiple client settlements.

