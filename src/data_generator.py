"""
Synthetic Dataset Generator for SettleSense.
Produces 240 deterministic securities settlement exception cases using seed 42:
- 210 labelled cases across 6 canonical categories (35 per category, 7 distinct scenario families per category, 5 variants per family)
- 30 ambiguous cases (UNDETERMINED category, is_sufficiently_informative=False)
Features natural linguistic diversity, realistic overlapping financial terminology,
and scenario-family grouping to prevent train/test leakage.
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pandas as pd

from config.settings import (
    DATA_DIR,
    RANDOM_SEED,
    CANONICAL_CATEGORIES,
    AMBIGUOUS_LABEL,
)

COUNTERPARTIES = [
    "Meridian Global Custody", "Apex Prime Brokerage", "Helios Capital Markets",
    "Nordic Sovereign Clearing", "Vanguard Settlement Agent", "Atlas Clearing Services",
    "Zephyr Securities UK", "Pacific Rim Nominees", "Crestview Asset Management",
    "Borealis Investment Banking", "Citadel Execution Trust", "Orion Custody SA",
    "Kallisto Asset Clearing", "Starlight Merchant Bank", "Solstice Securities Europe"
]

CURRENCIES = ["USD", "EUR", "GBP", "CHF", "JPY", "CAD", "SEK", "AUD"]

DEPOSITORIES = [
    "Euroclear Bank Brussels", "Clearstream Banking Luxembourg", "Depository Trust Company (DTC)",
    "Euroclear UK & International (CREST)", "SIX SIS Switzerland", "Monte Titoli Milan",
    "Iberclear Madrid", "Clearstream Frankfurt (CBF)"
]

TRADE_TYPES = [
    "EQUITY_DVP", "EQUITY_FOP", "GOVT_BOND_DVP", "CORP_BOND_DVP",
    "CROSS_BORDER_DVP", "REPO_CLOSING", "ETF_CREATION_UNIT", "DEPOSITORY_RECEIPT"
]

STATUSES = [
    "REJECTED_CSD", "UNMATCHED_MATCHING_UTILITY", "PENDING_INSUFFICIENT_POSITION",
    "FAILED_SETTLEMENT_CUTOFF", "HELD_OPERATIONS_QUEUE", "SUSPENDED_DISCREPANCY",
    "RECYCLED_CASH_DEFICIT", "UNCONFIRMED_ALLEGEMENT"
]

BICS = ["BANAUS33", "CHASSX22", "CITIUS33", "BNPAFRPP", "MIDLGB22", "DEUTDEDM", "UBSAFFZH", "SCBLSG22"]


def _generate_ssi_narrative(fam_idx: int, var_idx: int, cparty: str, curr: str, csd: str, trade_type: str, isin: str, qty: int, amount_str: str, trade_ref: str, rng: random.Random) -> Tuple[str, str]:
    """Generates distinct, diverse SSI mismatch narratives across 7 scenario families."""
    procedures = "PROC_01|PROC_02"
    acc1 = f"SAFEKEEP-{rng.randint(1000, 9999)}"
    acc2 = f"DEP-{rng.randint(10000, 99999)}"
    bic1 = rng.choice(BICS[:4])
    bic2 = rng.choice(BICS[4:])

    if fam_idx == 1:
        # Theme: Safekeeping account mismatch
        templates = [
            f"Depository status MT548 from {csd} reported settlement rejection on {trade_type} {trade_ref} for {amount_str}. Counterparty {cparty} delivered against depository account {acc2}, whereas internal trade record routed to custody account {acc1}. Economics and nominal quantity of {qty:,} shares in {isin} were confirmed agreed.",
            f"Settlement failed at {csd} for ticket {trade_ref} in {isin}. Our back office instructed delivery to omnibus account {acc1}, but broker {cparty} specified clearing account {acc2}. Cash funding and trade date were verified, but the depository rejected due to safekeeping account discrepancy.",
            f"NACK received from clearing agent {csd} on transaction {trade_ref}. The trade with {cparty} could not settle because the counterparty settlement advice specified account {acc2}, conflicting with our internal SSI register which designates {acc1}.",
            f"Instruction mismatch exception on {trade_type} {trade_ref}. Safekeeping account number {acc2} on {cparty}'s instruction differs from standing settlement instruction {acc1} on file at {csd} for {isin}. Transaction amount of {amount_str} remains queued.",
            f"Custody exception notice: Delivery of {qty:,} units of {isin} against {amount_str} was rejected by {csd}. Internal records indicate safekeeping account {acc1}, whereas incoming advice from {cparty} cites depository account {acc2}."
        ]
        evidence = f"Depository/safekeeping account mismatch between internal record ({acc1}) and counterparty {cparty} ({acc2}) at {csd} for {trade_ref}."

    elif fam_idx == 2:
        # Theme: Clearing agent BIC code mismatch
        templates = [
            f"Instruction routing discrepancy on trade {trade_ref} with {cparty} for {isin}. The clearing broker advised BIC code {bic1} in the receiving agent field, but internal trade capture designated settlement agent BIC {bic2}. Depository {csd} rejected the instruction citing an unrecognised beneficiary agent.",
            f"Bilateral instruction conflict on {trade_type} {trade_ref}. Internal operations routed settlement through clearing agent BIC {bic2} at {csd}, whereas incoming confirmation from {cparty} specified clearing agent BIC {bic1}. Trade consideration of {amount_str} is blocked at clearing.",
            f"Settlement gateway alert: MT541 instruction for {isin} rejected by {csd}. Receiving agent BIC code {bic1} transmitted by {cparty} does not correspond to our designated custodian BIC {bic2}. Trade date and share quantity of {qty:,} match bilateral records.",
            f"Depository matching failed for ticket {trade_ref} with {cparty}. Our instruction designated agent BIC {bic2}, while counterparty's clearing desk instructed through BIC {bic1} at {csd}. The depository matching utility flagged receiving agent inconsistency.",
            f"Agent bank mismatch on {trade_type} in {isin}. Internal records confirm trade terms of {amount_str} with {cparty}, but our back office instructed via agent {bic2} while {cparty} routed to agent {bic1}."
        ]
        evidence = f"Receiving agent BIC code inconsistency ({bic1} vs {bic2}) between internal instruction and counterparty {cparty} at {csd} on {trade_ref}."

    elif fam_idx == 3:
        # Theme: Decommissioned SSI version / quarter-end transition
        v_old = rng.randint(1, 2)
        v_new = rng.randint(3, 4)
        templates = [
            f"Settlement instruction rejection received from {csd} for ticket {trade_ref}. The trade in {isin} with {cparty} was booked under SSI version {v_old}, but market rules required decommissioned SSI version {v_new} following the quarterly transition. Clearing accounts conflict between bilateral files.",
            f"SSI version conflict flagged on {trade_type} {trade_ref} involving {qty:,} units of {isin}. Counterparty {cparty} instructed settlement under legacy instruction profile v{v_old}, while our system updated to v{v_new} on the first of the month.",
            f"Depository rejection: 'Expired Standing Instruction'. Trade {trade_ref} for {amount_str} failed matching at {csd} because {cparty} utilized an outdated SSI release code. Updated golden-source standing instructions were published two weeks ago.",
            f"Instruction lifecycle exception: Custodian {csd} rejected delivery of {isin} to {cparty}. Our operations desk transmitted under active SSI profile v{v_new}, but the counterparty matched against legacy profile v{v_old} which was retired prior to trade date.",
            f"Bilateral SSI version misalignment on order {trade_ref}. Ticket for {amount_str} was rejected at {csd} because {cparty} referenced effective SSI schedule v{v_old} rather than the revised schedule v{v_new} agreed for this currency."
        ]
        evidence = f"SSI version discrepancy (v{v_old} vs v{v_new}) between bilateral records for {cparty} at {csd} on {trade_ref}."

    elif fam_idx == 4:
        # Theme: Omnibus vs Segregated sub-custodian account routing
        sub_acc = f"SUB-SEG-{rng.randint(20000, 89999)}"
        omni_acc = f"OMNI-CLR-{rng.randint(10000, 49999)}"
        templates = [
            f"Custodian status message MT548 for ticket {trade_ref} indicates 'NACK: Invalid Safekeeping Account'. We instructed delivery of {qty:,} shares of {isin} against {amount_str} to omnibus account {omni_acc} at {csd}, but counterparty {cparty} requires settlement into segregated sub-custodian account {sub_acc}.",
            f"Routing conflict on {trade_type} {trade_ref} with {cparty}. Counterparty settlement mandate requires direct delivery to segregated sub-custody account {sub_acc}, but internal order management system defaulted to general omnibus clearing account {omni_acc} at {csd}.",
            f"Depository exception at {csd} on {trade_ref}: Sub-custodian account inconsistency. The instruction in {isin} for {cparty} failed because internal booking utilized omnibus pool {omni_acc} instead of client segregated ledger {sub_acc}.",
            f"Instruction rejection notice: Trade {trade_ref} for {amount_str} in {isin} was halted at {csd}. Counterparty {cparty} advised segregated safekeeping account {sub_acc}, whereas our automated settlement engine routed to omnibus account {omni_acc}.",
            f"Safekeeping segregation error on order {trade_ref}. Internal operations advised omnibus clearing depository {omni_acc} at {csd}, but counterparty {cparty} rejected the instruction citing missing sub-account segregation code {sub_acc}."
        ]
        evidence = f"Sub-custodian account routing mismatch: omnibus account {omni_acc} instructed instead of segregated account {sub_acc} for {cparty} on {trade_ref}."

    elif fam_idx == 5:
        # Theme: Triparty collateral account routing
        tri_acc = f"TRIPARTY-{rng.randint(3000, 7999)}"
        templates = [
            f"Triparty repo settlement exception on ticket {trade_ref} with {cparty}. Collateral allocation of {qty:,} units of {isin} failed at {csd} because our instruction routed to standard settlement account instead of designated triparty collateral account {tri_acc}.",
            f"Depository alert on {trade_type} {trade_ref}: Invalid collateral account. Internal trade booking for {amount_str} omitted the counterparty's triparty collateral safekeeping identifier {tri_acc} at {csd}, causing instruction rejection.",
            f"Settlement instruction rejected by {csd} on order {trade_ref}. Collateral transfer in {isin} with {cparty} could not be completed because internal instruction failed to designate the agreed triparty escrow account {tri_acc}.",
            f"Collateral management exception on trade {trade_ref}. Custodian {csd} rejected settlement of {amount_str} with {cparty} due to mismatched triparty clearing participant and account code {tri_acc}.",
            f"Instruction format rejection on repo ticket {trade_ref}. Triparty agent at {csd} flagged missing collateral partition identifier for {cparty}, routing instead to commercial safekeeping account {acc1}."
        ]
        evidence = f"Triparty collateral account omission/mismatch: instruction failed to specify collateral account {tri_acc} for {cparty} at {csd} on {trade_ref}."

    elif fam_idx == 6:
        # Theme: Domestic CSD vs International ICSD venue mismatch
        templates = [
            f"Cross-border depository location conflict on {trade_type} {trade_ref} for {isin}. Internal settlement desk routed instruction to international depository {csd}, while counterparty {cparty} instructed settlement in domestic market clearing. Instructions remain unlinked.",
            f"Settlement venue discrepancy on trade ticket {trade_ref}. Counterparty {cparty} expects delivery of {qty:,} shares of {isin} against {amount_str} in local domestic depository, but internal trade capture designated ICSD clearing at {csd}.",
            f"Depository routing exception on order {trade_ref} with {cparty}. Our instruction was lodged at {csd}, whereas incoming matching allegement from {cparty} was lodged in domestic central depository. Bilateral bridge transfer was not established.",
            f"Clearing location mismatch for {trade_type} in {isin}. Internal records confirm consideration of {amount_str} with {cparty}, but internal operations dispatched to {csd} while broker instructed domestic market depository.",
            f"Bilateral bridge failure on trade {trade_ref}. Trade for {isin} with {cparty} failed matching because our back office instructed via {csd} without configuring the domestic depository link."
        ]
        evidence = f"Settlement location mismatch: internal instruction routed to {csd} while counterparty {cparty} instructed in domestic clearing for {trade_ref}."

    else:
        # Theme: Unauthorized / Unauthenticated SSI change
        templates = [
            f"Settlement block on trade {trade_ref} with {cparty} for {isin}. Counterparty settlement desk advised new banking coordinates via unauthenticated email, but internal compliance requires authenticated SWIFT MT599/standing instruction authorization before updating depository instructions at {csd}.",
            f"Unauthorized instruction amendment exception on {trade_type} {trade_ref}. Counterparty {cparty} requested delivery of {amount_str} to alternative account {acc2}, which conflicts with authorized master SSI on file at {csd}.",
            f"Compliance settlement hold on ticket {trade_ref} in {isin}. Trade with {cparty} for {qty:,} shares was halted because counterparty's advised delivery account does not match authorized standing instructions in the golden-source directory.",
            f"Security instruction dispute on order {trade_ref} at {csd}. Internal operations refused manual account override to account {acc2} requested by {cparty} pending formal authorized signatory verification.",
            f"Depository instruction held on trade {trade_ref}. Counterparty {cparty} submitted clearing details that deviate from master institutional SSI profile without authenticated documentation for {isin}."
        ]
        evidence = f"Unauthenticated SSI modification: counterparty {cparty} advised alternative account {acc2} conflicting with authorized master profile at {csd} on {trade_ref}."

    return templates[var_idx % len(templates)], evidence


def _generate_trade_detail_narrative(fam_idx: int, var_idx: int, cparty: str, curr: str, csd: str, trade_type: str, isin: str, qty: int, amount: float, amount_str: str, trade_ref: str, rng: random.Random) -> Tuple[str, str]:
    """Generates distinct, diverse Trade Detail mismatch narratives across 7 scenario families."""
    procedures = "PROC_03|PROC_04"
    diff_qty = qty + rng.choice([-2000, -1000, 500, 1500, 5000])
    diff_amt = round(amount * rng.uniform(0.91, 1.09), 2)
    diff_curr = rng.choice([c for c in CURRENCIES if c != curr])

    if fam_idx == 1:
        # Theme: Nominal quantity mismatch
        templates = [
            f"Central matching utility flagged nominal quantity discrepancy on {trade_type} {trade_ref} with {cparty}. Internal ledger records {qty:,} units of {isin}, whereas {cparty} submitted an allocation ticket specifying {diff_qty:,} units. Execution ticket indicates block allocation variance.",
            f"Trade quantity conflict on order {trade_ref} at {csd}. Our confirmation shows purchase of {qty:,} shares of {isin}, but counterparty {cparty} confirmed delivery of {diff_qty:,} shares. Settlement cannot proceed until nominal quantity is reconciled.",
            f"Matching discrepancy notice from CTM utility for {isin} on ticket {trade_ref}. Internal booking lists nominal quantity {qty:,}, while counterparty {cparty} alleges quantity {diff_qty:,}. Net consideration is consequently misaligned.",
            f"Bilateral quantity variance on {trade_type} {trade_ref} with {cparty}. Front office confirms agreed execution was for {qty:,} shares of {isin}, but counterparty trade capture blotter recorded {diff_qty:,} units.",
            f"Allocation mismatch exception: Trade ticket {trade_ref} in {isin} failed central matching. Our block allocation breakdown sums to {qty:,} shares, but broker {cparty} confirmed {diff_qty:,} shares across child accounts."
        ]
        evidence = f"Nominal quantity mismatch: internal booking ({qty:,}) vs counterparty {cparty} ({diff_qty:,}) on {trade_ref}."

    elif fam_idx == 2:
        # Theme: Consideration amount / Accrued interest conflict
        templates = [
            f"Trade matching exception at {csd} for {trade_ref}: consideration amount conflict. Internal ledger expects gross settlement amount of {amount_str} for {isin}, but incoming electronic confirmation from broker {cparty} specifies {diff_amt:,.2f} {curr}. Difference stems from divergent accrued interest and handling commission calculations.",
            f"Net settlement cash discrepancy on bond ticket {trade_ref} with {cparty}. Internal system calculated total consideration of {amount_str} for {isin}, whereas counterparty advised net cash of {diff_amt:,.2f} {curr}. Discrepancy exceeds CSD automatic matching tolerance.",
            f"Consideration mismatch alert: Central matching rejected trade {trade_ref} in {isin}. Our trade ticket specifies net amount {amount_str}, but {cparty} confirmed {diff_amt:,.2f} {curr}. Accrued interest day-count calculations diverge.",
            f"Financial consideration variance on {trade_type} {trade_ref}. Bilateral records agree on nominal {qty:,} shares of {isin}, but counterparty {cparty} calculated dirty consideration of {diff_amt:,.2f} {curr} vs internal figure {amount_str}.",
            f"Cash consideration conflict at {csd} on order {trade_ref}. Internal back office calculated settlement amount of {amount_str}, while broker {cparty} confirmed settlement amount of {diff_amt:,.2f} {curr} due to fee inclusion."
        ]
        evidence = f"Net consideration amount discrepancy: internal record ({amount_str}) vs counterparty {cparty} ({diff_amt:,.2f} {curr}) on {trade_ref}."

    elif fam_idx == 3:
        # Theme: Execution price discrepancy
        p1 = rng.uniform(25.0, 350.0)
        p2 = round(p1 + rng.uniform(0.75, 4.5), 3)
        templates = [
            f"Bilateral matching failure in {trade_type} {trade_ref}. We recorded execution price at {p1:.3f} {curr} for {isin}, whereas counterparty {cparty} confirmed at execution price of {p2:.3f} {curr}. Trading desk states verbal order recap was amended without electronic ticket update.",
            f"Price discrepancy exception flagged on trade {trade_ref} with {cparty}. Front office booked {qty:,} shares of {isin} at price {p1:.3f} {curr}, but counterparty's execution report cites price {p2:.3f} {curr}. Trade consideration cannot match at {csd}.",
            f"Matching utility returned status 'PRICE_MISMATCH' on order {trade_ref} in {isin}. Internal records confirm price of {p1:.3f} {curr}, while broker {cparty} confirmed price of {p2:.3f} {curr}.",
            f"Execution price disagreement on ticket {trade_ref} with {cparty}. Our trader booked execution at {p1:.3f} {curr}, while counterpart dealer confirmed at {p2:.3f} {curr}. Total variance is {abs(amount - diff_amt):,.2f} {curr}.",
            f"Deal recap conflict: Trade {trade_ref} for {qty:,} units of {isin} rejected by matching engine. Price variance between internal booking ({p1:.3f} {curr}) and counterparty confirmation ({p2:.3f} {curr}) exceeds tolerance threshold."
        ]
        evidence = f"Execution price mismatch: internal booking ({p1:.3f} {curr}) vs counterparty {cparty} ({p2:.3f} {curr}) on {trade_ref}."

    elif fam_idx == 4:
        # Theme: Settlement currency mismatch
        templates = [
            f"Central matching utility CTM returned status 'DISCREPANCY' for {isin} on trade {trade_ref}. Internal records indicate settlement currency {curr}, but counterparty {cparty} booked the settlement leg denominated in {diff_curr}. ISIN and trade date match, but currency conflict prevents settlement.",
            f"Settlement currency conflict on ticket {trade_ref} with {cparty}. Our trade capture blotter specifies settlement in {curr} for {isin}, whereas incoming counterparty confirmation specifies settlement in {diff_curr}. CSD {csd} cannot pair instructions with opposing currency codes.",
            f"Currency code mismatch alert on {trade_type} {trade_ref}. Bilateral records agree on nominal quantity {qty:,} of {isin}, but counterparty {cparty} instructed payment in {diff_curr} while internal instruction designated {curr}.",
            f"Depository pairing rejection at {csd} for order {trade_ref}. Trade consideration currency code was submitted as {curr} by our back office, but counterpart clearing broker {cparty} submitted instruction denominated in {diff_curr}.",
            f"Bilateral currency discrepancy on trade {trade_ref} in {isin}. Counterparty {cparty} confirmed settlement consideration in {diff_curr}, conflicting with our front-office order ticket denominated in {curr}."
        ]
        evidence = f"Settlement currency code mismatch: internal record ({curr}) vs counterparty {cparty} ({diff_curr}) on {trade_ref}."

    elif fam_idx == 5:
        # Theme: Security identifier / share class mismatch
        alt_isin = f"{isin[:2]}{rng.randint(100000000, 999999999)}"
        templates = [
            f"Reconciliation alert: Security identifier mismatch on trade ticket {trade_ref} with {cparty}. Internal booking references ISIN {isin}, whereas counterparty's clearing confirmation cites alternative class identifier {alt_isin}. Quantity of {qty:,} shares and trade date align, but security master records distinct share classes.",
            f"Share class confusion on order {trade_ref} at {csd}. Our trading desk booked voting ordinary shares under ISIN {isin}, but counterparty {cparty} submitted confirmation for non-voting class B shares under ISIN {alt_isin}.",
            f"Security master discrepancy notice: Trade {trade_ref} with {cparty} failed matching. Internal records cite security identifier {isin}, whereas incoming confirmation from broker cites {alt_isin}. Quantity and net consideration align.",
            f"ISIN mismatch on {trade_type} {trade_ref}. Counterparty {cparty} instructed delivery of security {alt_isin}, but our custody account expects receipt of {isin}. Depository {csd} rejected paired matching.",
            f"Instrument classification exception on ticket {trade_ref} with {cparty}. Front office execution recap cites ISIN {isin}, while counterparty clearing blotter allocated trade under alternative identifier {alt_isin}."
        ]
        evidence = f"Security identifier / share class discrepancy: internal ISIN {isin} vs counterparty {cparty} ISIN {alt_isin} on {trade_ref}."

    elif fam_idx == 6:
        # Theme: Trade date / Execution timestamp disagreement
        templates = [
            f"Trade date discrepancy on order {trade_ref} with {cparty} in {isin}. Our booking records execution on trade date T, whereas counterparty's electronic confirmation cites trade date T-1. Central matching engine rejected the trade as unaligned.",
            f"Execution date conflict on {trade_type} {trade_ref} for {amount_str}. Counterparty {cparty} confirmed trade date of Monday, while internal trade blotter recorded trade date of Tuesday following late-night allocation.",
            f"Matching utility alert on ticket {trade_ref} in {isin}. Discrepancy detected in execution timestamp between internal record and broker {cparty}, blocking automatic contract generation at {csd}.",
            f"Trade date mismatch exception on order {trade_ref} with {cparty}. Trade terms in {isin} for {qty:,} shares cannot pair because counterparty instructed under a different contractual trade date.",
            f"Bilateral trade date variance on {trade_type} {trade_ref}. Internal operations records trade execution date as 14th, while counterparty {cparty} submitted matching ticket with trade execution date of 15th."
        ]
        evidence = f"Trade execution date conflict between internal booking and counterparty {cparty} on {trade_ref}."

    else:
        # Theme: Commission / Tax fee inclusion disagreement
        templates = [
            f"Fee schedule discrepancy on {trade_type} {trade_ref} with {cparty}. Internal ledger booked net consideration of {amount_str} clean of commissions, while counterparty {cparty} added local stamp duty and brokerage fees into the gross settlement amount.",
            f"Settlement cash variance on ticket {trade_ref} in {isin}. Broker {cparty} added market execution levy of {abs(amount - diff_amt):,.2f} {curr} to settlement amount, whereas internal trading desk instructed net flat consideration.",
            f"Commission accounting conflict on order {trade_ref} at {csd}. Trade for {qty:,} units was rejected because counterparty {cparty} deducted withholding tax at source, whereas our booking expects gross settlement of {amount_str}.",
            f"Bilateral fee calculation mismatch on trade {trade_ref} with {cparty}. Our confirmation specifies net settlement consideration {amount_str}, but {cparty} instructed consideration with embedded broker clearing commission.",
            f"Matching dispute on ticket {trade_ref} in {isin}. Counterparty {cparty} confirmed trade amount including market transaction tax, causing consideration variance against internal net settlement booking."
        ]
        evidence = f"Fee/tax inclusion mismatch: counterparty {cparty} embedded commissions/taxes into consideration vs internal net booking on {trade_ref}."

    return templates[var_idx % len(templates)], evidence


def _generate_securities_shortfall_narrative(fam_idx: int, var_idx: int, cparty: str, curr: str, csd: str, trade_type: str, isin: str, qty: int, amount_str: str, trade_ref: str, rng: random.Random) -> Tuple[str, str]:
    """Generates distinct, diverse Securities Shortfall narratives across 7 scenario families."""
    procedures = "PROC_05|PROC_06"
    avail_qty = max(0, qty - rng.randint(600, qty // 2 if qty > 1200 else 600))

    if fam_idx == 1:
        # Theme: General vault inventory deficit
        templates = [
            f"Custodian status notification from {csd} for ticket {trade_ref} indicates 'Settlement Pending: Insufficient Securities Balance'. Delivery of {qty:,} units of {isin} against {amount_str} to {cparty} is suspended because available settled balance in our safekeeping account is only {avail_qty:,} shares.",
            f"Outbound delivery failure for {trade_type} {trade_ref} involving {qty:,} shares of {isin}. Real-time custody ledger at {csd} shows deficit of {qty - avail_qty:,} shares against delivery commitments to {cparty}. Available unencumbered inventory is depleted.",
            f"Depository instruction for {trade_ref} representing {amount_str} against {isin} recycled continuously. Custodian {csd} confirmed our account lacks unencumbered inventory to deliver {qty:,} units to counterparty {cparty}.",
            f"Settlement exception alert: Insufficient stock for {isin} on order {trade_ref} at {csd}. Our custody balance shows only {avail_qty:,} shares available to satisfy delivery obligation of {qty:,} shares to {cparty}.",
            f"Delivery vs Payment (DvP) instruction {trade_ref} failed at {csd}. Counterparty {cparty} is positioned to receive {qty:,} units of {isin}, but our sub-custodian reports insufficient free settled position."
        ]
        evidence = f"Unencumbered inventory deficit for {isin} at {csd}: available balance ({avail_qty:,}) below delivery requirement ({qty:,}) on {trade_ref}."

    elif fam_idx == 2:
        # Theme: Upstream purchase fail causing downstream shortfall
        templates = [
            f"Settlement queue block on outbound trade {trade_ref} for {isin} to {cparty}. Expected inbound purchase of {qty:,} shares from another broker failed to settle during the morning cycle at {csd}, leaving our inventory deficient to complete downstream delivery.",
            f"Chain settlement failure impacting ticket {trade_ref}. Delivery of {qty:,} units of {isin} against {amount_str} to {cparty} is failing because our delivering broker on the upstream purchase leg failed to deliver securities.",
            f"Inventory dependency failure at {csd} on order {trade_ref}. Downstream delivery of {isin} to {cparty} is stalled; custodian confirms incoming street-side receipt trade remains unsettled, resulting in inventory shortfall.",
            f"Depository recycling exception on trade {trade_ref}. We cannot deliver {qty:,} shares of {isin} to counterparty {cparty} because upstream street delivery failed to arrive before the depository batch run.",
            f"Outbound delivery halted on order {trade_ref} in {isin}. Back office notes downstream delivery to {cparty} depends on incoming purchase from clearing broker that failed settlement earlier today."
        ]
        evidence = f"Upstream purchase fail: failed incoming receipt created downstream inventory shortfall for delivery of {isin} to {cparty} on {trade_ref}."

    elif fam_idx == 3:
        # Theme: Stock borrow locate / lending allocation pending
        templates = [
            f"Depository instruction {trade_ref} for {amount_str} against {isin} recycled throughout the afternoon. Custodian {csd} confirmed account lacks inventory to deliver {qty:,} units to {cparty}. Securities lending desk submitted stock borrow request, but loan allocation remains pending.",
            f"Stock borrow allocation delay on ticket {trade_ref} with {cparty}. Outbound short sale delivery of {qty:,} shares of {isin} is failing at {csd} because our borrowing agent has not yet confirmed the locate transfer.",
            f"Settlement fail warning on order {trade_ref} in {isin}. Our inventory balance is zero, and the pre-borrow contract booked to deliver {qty:,} shares to {cparty} has not posted to our safekeeping account at {csd}.",
            f"Lending desk delay on trade {trade_ref}. Delivery of {isin} against {amount_str} to {cparty} is suspended at {csd} pending execution of securities borrow ticket to cover inventory deficit.",
            f"Unallocated stock loan on order {trade_ref}. Counterparty {cparty} is awaiting receipt of {qty:,} units of {isin}, but securities lending operations has not confirmed borrow delivery into our vault."
        ]
        evidence = f"Stock borrow allocation pending: securities lending locate not yet delivered to cover short position for {cparty} on {trade_ref}."

    elif fam_idx == 4:
        # Theme: Corporate action escrow lockup
        templates = [
            f"Settlement exception alert: Insufficient free stock for {isin} on order {trade_ref} at {csd}. Internal records show total holding of {qty:,} shares, but {qty - avail_qty:,} units are currently locked in a mandatory corporate action exchange escrow, leaving free delivery balance below requirement for {cparty}.",
            f"Corporate action restriction on ticket {trade_ref} with {cparty}. Delivery of {qty:,} shares of {isin} failed at {csd} because custodian froze position pending completion of voluntary tender offer election.",
            f"Position encumbrance exception on order {trade_ref} in {isin}. Total position covers trade obligation of {amount_str}, but shares are immobilized in depository corporate action account, blocking transfer to {cparty}.",
            f"Depository freeze on trade {trade_ref}. Transfer of {qty:,} units of {isin} to {cparty} was rejected by {csd} due to ongoing rights issue record date restriction on safekeeping balance.",
            f"Custody position locked for ticket {trade_ref}. Shares in {isin} owed to {cparty} are currently segregated in corporate re-organization escrow at {csd}, preventing settlement release."
        ]
        evidence = f"Corporate action escrow lockup: shares in {isin} immobilized in custody escrow, preventing delivery to {cparty} on {trade_ref}."

    elif fam_idx == 5:
        # Theme: Collateral pledge encumbrance
        templates = [
            f"Depository status notice for order {trade_ref} at {csd}: Insufficient unencumbered position. Internal records show nominal holding of {qty:,} shares of {isin}, but balance is pledged as collateral with central clearing house, preventing delivery of {qty:,} shares to {cparty}.",
            f"Collateral pledge encumbrance on ticket {trade_ref}. Delivery of {isin} against {amount_str} to {cparty} failed because target position was automatically swept into our intraday margin buffer at {csd}.",
            f"Pledged inventory restriction on order {trade_ref} in {isin}. Safekeeping account holds {qty:,} shares, but custodian confirmed securities are encumbered under tri-party repo pledge, leaving zero free balance for {cparty}.",
            f"Margin pool lockup on trade {trade_ref}. Settlement of {qty:,} units of {isin} to {cparty} is blocked at {csd} because shares are currently assigned as collateral against derivative clearing margin.",
            f"Inventory encumbrance on order {trade_ref}. Back office notes that while {isin} balance appears on ledger, securities are pledged under credit facility and cannot be released to {cparty}."
        ]
        evidence = f"Collateral pledge encumbrance: shares in {isin} pledged to clearing margin pool, leaving insufficient free balance for {cparty} on {trade_ref}."

    elif fam_idx == 6:
        # Theme: Multi-depository inventory fragmentation / Inter-CSD realignment needed
        templates = [
            f"Inventory location fragmentation on ticket {trade_ref} for {isin}. Counterparty {cparty} is awaiting delivery at {csd}, but our inventory of {qty:,} shares is located at an alternate European depository. Inter-CSD realignment transfer is required.",
            f"Depository realignment delay on order {trade_ref} with {cparty}. Our position in {isin} is sufficient across global vaults, but local safekeeping balance at {csd} is zero. Free-of-payment bridge transfer has not settled.",
            f"Cross-depository inventory deficit on trade {trade_ref}. Delivery of {qty:,} units of {isin} to {cparty} failed at {csd} because target position remains held in US vault rather than European depository.",
            f"Custody vault misalignment on ticket {trade_ref}. Internal operations confirmed overall company position in {isin} covers delivery of {amount_str}, but inventory is fragmented across multiple sub-custodians.",
            f"Inter-depository transfer pending on order {trade_ref}. Transfer of {isin} to {cparty} failed at {csd} due to lack of local inventory while bridge realignment from domestic depository is in transit."
        ]
        evidence = f"Inventory fragmentation: securities in {isin} held at alternate vault; inter-CSD realignment to {csd} required for {cparty} on {trade_ref}."

    else:
        # Theme: CSDR Settlement Discipline Penalty Warning due to lack of securities
        templates = [
            f"CSDR settlement fail penalty warning triggered on order {trade_ref} at {csd}. Delivery of {qty:,} shares of {isin} to {cparty} is failing on consecutive settlement cycles due to ongoing inventory deficit in safekeeping account.",
            f"Settlement discipline penalty notice for ticket {trade_ref} in {isin}. Depository {csd} issued daily cash penalty against our account as delivery of {amount_str} to {cparty} remains unfulfilled due to position deficit.",
            f"Regulatory penalty alert on order {trade_ref} with {cparty}. Persistent lack of deliverable shares in {isin} at {csd} has placed transaction into mandatory buy-in warning timeline.",
            f"Depository penalty escalation on trade {trade_ref}. Our delivery of {qty:,} units of {isin} to {cparty} failed third consecutive cycle at {csd} due to lack of securities inventory.",
            f"Buy-in risk notification on order {trade_ref}. Counterparty {cparty} has threatened mandatory buy-in execution for {isin} as our safekeeping account at {csd} continues to experience inventory deficit."
        ]
        evidence = f"CSDR fail penalty & persistent inventory deficit: consecutive settlement fails in {isin} to {cparty} at {csd} on {trade_ref}."

    return templates[var_idx % len(templates)], evidence


def _generate_cash_shortfall_narrative(fam_idx: int, var_idx: int, cparty: str, curr: str, csd: str, trade_type: str, isin: str, qty: int, amount: float, amount_str: str, trade_ref: str, rng: random.Random) -> Tuple[str, str]:
    """Generates distinct, diverse Cash Shortfall narratives across 7 scenario families."""
    procedures = "PROC_07|PROC_08"
    avail_amt = round(amount * rng.uniform(0.08, 0.55), 2)
    shortfall_amt = round(amount - avail_amt, 2)

    if fam_idx == 1:
        # Theme: Intraday credit cap / debit cap limit breach
        templates = [
            f"DvP settlement {trade_ref} in {csd} halted due to liquidity restriction. Our designated settlement Nostro bank advises that our intraday debit cap has been reached, preventing payment of {amount_str} to counterparty {cparty}. Treasury operations has been notified to execute liquidity injection.",
            f"Debit limit cap exceeded on settlement account at {csd} for ticket {trade_ref}. Net consideration of {amount_str} payable to {cparty} for {isin} was blocked because our intraday overdraft facility has reached maximum ceiling.",
            f"Cash clearing agent rejected payment on order {trade_ref} with {cparty}. Nostro account debit limit in {curr} breached following high-value morning payment batches, preventing settlement of {amount_str}.",
            f"Liquidity ceiling exception on {trade_type} {trade_ref}. Settlement of {qty:,} shares of {isin} cannot complete because our clearing agent bank placed cap on additional debit disbursements in {curr}.",
            f"Intraday credit line exhausted at {csd} on ticket {trade_ref}. Outstanding payment of {amount_str} to {cparty} was rejected by settlement bank due to bilateral credit cap exhaustion."
        ]
        evidence = f"Intraday credit cap / debit ceiling breached at settlement bank, blocking payment of {amount_str} to {cparty} on {trade_ref}."

    elif fam_idx == 2:
        # Theme: Insufficient settled cash in Nostro account
        templates = [
            f"Cash clearing agent reported settlement failure on receive-versus-payment transaction {trade_ref} for {isin}. Nostro cash account in {curr} holds available balance of {avail_amt:,.2f} {curr}, which is insufficient to cover required net consideration of {amount_str} owed to {cparty}.",
            f"Insufficient funds notification from clearing bank for ticket {trade_ref}. Consideration payment of {amount_str} in favor of {cparty} was dishonored due to shortfall of {shortfall_amt:,.2f} {curr} in our {curr} Nostro account.",
            f"Settlement exception on {trade_ref}: Payment message MT202 for {amount_str} in favor of {cparty} was rejected by clearing bank due to lack of settled funds in {curr} Nostro account. Security receipt in {isin} is queued awaiting funding release.",
            f"Nostro balance deficit on order {trade_ref} at {csd}. Available cash ledger indicates balance of {avail_amt:,.2f} {curr}, leaving shortfall against payment obligation of {amount_str} to {cparty}.",
            f"Payment queue block: Clearing bank placed hold on outbound settlement transfer {trade_ref} for {trade_type} with {cparty}. Outstanding cash balance in {curr} is short by {shortfall_amt:,.2f} {curr}."
        ]
        evidence = f"Insufficient settled cash in {curr} Nostro account: available ({avail_amt:,.2f} {curr}) below required consideration ({amount_str}) for {cparty} on {trade_ref}."

    elif fam_idx == 3:
        # Theme: Currency wire delayed at correspondent bank (AML/compliance review)
        templates = [
            f"Inbound currency wire funding settlement account at {csd} is delayed at correspondent bank. Payment of {amount_str} owed to {cparty} on ticket {trade_ref} in {isin} cannot be released until intermediary bank completes compliance screening on funding transfer.",
            f"Correspondent banking delay on trade {trade_ref}. Currency wire for {amount_str} intended to fund our {curr} Nostro was held for AML review by clearing agent, leaving settlement account unfunded for {cparty}.",
            f"Funding transfer stalled on order {trade_ref} in {isin}. Intermediary correspondent bank placed administrative hold on our {amount_str} cash transfer, causing settlement fail with {cparty} at {csd}.",
            f"SWIFT payment delay impacting settlement ticket {trade_ref}. Funding wire to settlement account is delayed at correspondent gateway, resulting in cash deficit for trade with {cparty}.",
            f"Correspondent screening block on order {trade_ref}. Settlement of {qty:,} units of {isin} against {amount_str} failed at {csd} because correspondent bank held inbound cash transfer pending beneficiary confirmation."
        ]
        evidence = f"Inbound currency funding wire delayed at correspondent bank for compliance review, leaving Nostro unfunded for {cparty} on {trade_ref}."

    elif fam_idx == 4:
        # Theme: Inbound FX funding swap cutoff elapsed
        templates = [
            f"Currency funding cutoff elapsed before incoming FX swap could fund local settlement Nostro at {csd} for ticket {trade_ref}. The trade consideration of {amount_str} payable to {cparty} in {isin} remains unfunded. Local central bank payment wire cutoff was reached at 16:00 local time.",
            f"FX conversion delay on order {trade_ref} with {cparty}. Foreign exchange swap booked to cover {amount_str} in {curr} settled past the local payment clearing cutoff, leaving settlement account in deficit.",
            f"Cross-currency funding cutoff missed on trade {trade_ref}. Our treasury FX desk executed currency conversion for {amount_str}, but payment instructions missed the same-day settlement cutoff for {curr} at {csd}.",
            f"Liquidity cutoff exception on ticket {trade_ref} in {isin}. Inbound FX swap funds arrived 20 minutes past the depository cash settlement window, leaving payment to {cparty} unfunded.",
            f"Currency swap settlement failure impacting order {trade_ref}. Back office confirmed FX leg missed the RTGS cutoff window, preventing cash disbursement of {amount_str} to {cparty}."
        ]
        evidence = f"FX swap funding cutoff elapsed prior to cash clearing window, leaving consideration of {amount_str} unfunded for {cparty} on {trade_ref}."

    elif fam_idx == 5:
        # Theme: Cash depleted following high-value bond redemption debits
        templates = [
            f"Unexpected cash drain on settlement Nostro impacted ticket {trade_ref} with {cparty}. Overnight corporate bond redemption debit drained {curr} cash pool, leaving insufficient liquidity to settle {amount_str} for {isin} at {csd}.",
            f"Liquidity pool depletion on order {trade_ref}. Prior settlement debits from corporate bond coupon runs consumed available cash in {curr}, resulting in automated settlement hold for {amount_str} owed to {cparty}.",
            f"Nostro cash deficit on trade {trade_ref} in {isin}. Prior settlement obligations exhausted available intraday cash buffer, preventing DvP settlement of {amount_str} with broker {cparty} at {csd}.",
            f"Account cash deficit following high-volume payments on order {trade_ref}. Scheduled disbursements earlier in the cycle depleted account balance, leaving {shortfall_amt:,.2f} {curr} shortfall for {cparty}.",
            f"Unforeseen cash balance depletion on ticket {trade_ref}. Settlement bank reported insufficient funds to execute payment of {amount_str} to {cparty} due to earlier batch settlement deductions."
        ]
        evidence = f"Settlement cash depleted by prior payment debits, leaving insufficient funds ({amount_str}) for {cparty} on {trade_ref}."

    elif fam_idx == 6:
        # Theme: Central bank gross settlement queue hold (TARGET2 / Fedwire reserve deficit)
        templates = [
            f"Central bank payment queue hold on ticket {trade_ref} with {cparty}. Real-time gross settlement system placed payment of {amount_str} for {isin} in central bank queue due to reserve balance limits at clearing agent.",
            f"RTGS liquidity reservation hold on order {trade_ref}. Central bank clearing system halted outbound transfer of {amount_str} to {cparty} pending top-up of clearing agent settlement reserve.",
            f"National payment system queue exception on trade {trade_ref}. Payment message for {amount_str} in {isin} was queued at central bank settlement gateway due to intraday balance shortfall.",
            f"Central bank settlement hold impacting order {trade_ref} at {csd}. Transfer of {amount_str} to counterparty {cparty} is held in payment queue awaiting clearing bank reserve replenishment.",
            f"High-value payment queue delay on ticket {trade_ref}. Gross settlement transfer in {curr} for {cparty} remains pending at central bank gateway due to participant liquidity cap."
        ]
        evidence = f"Central bank gross settlement queue hold due to clearing agent reserve balance deficit on {amount_str} for {cparty} on {trade_ref}."

    else:
        # Theme: Cross-currency mismatch between trading and funding currency
        templates = [
            f"Currency funding mismatch on ticket {trade_ref} with {cparty}. Front office trade is denominated in {curr}, but treasury funded Nostro account in alternate currency, resulting in lack of settled {curr} funds at {csd} to cover {amount_str}.",
            f"Currency allocation error on order {trade_ref}. Settlement desk held funds in USD rather than required settlement currency {curr}, leaving trade obligation of {amount_str} in {isin} unfunded for {cparty}.",
            f"Settlement account funding currency conflict on trade {trade_ref}. Broker {cparty} requires settlement in {curr}, but internal treasury transfer posted to euro ledger, creating a funding deficit at {csd}.",
            f"Funding currency misdirection on order {trade_ref} in {isin}. Back office confirmed liquidity transfer of {amount_str} was routed to incorrect currency nostro, leaving primary settlement account short.",
            f"Currency ledger mismatch on ticket {trade_ref} with {cparty}. Nostro account in {curr} experienced payment rejection because cash injection was credited to foreign exchange ledger."
        ]
        evidence = f"Cross-currency funding misdirection: settlement Nostro in {curr} unfunded due to currency allocation error for {cparty} on {trade_ref}."

    return templates[var_idx % len(templates)], evidence


def _generate_counterparty_unconfirmed_narrative(fam_idx: int, var_idx: int, cparty: str, curr: str, csd: str, trade_type: str, isin: str, qty: int, amount_str: str, trade_ref: str, rng: random.Random) -> Tuple[str, str]:
    """Generates distinct, diverse Counterparty Unconfirmed narratives across 7 scenario families."""
    procedures = "PROC_09|PROC_10"

    if fam_idx == 1:
        # Theme: Unmatched status on central matching utility with zero incoming allegements
        templates = [
            f"Trade {trade_ref} remains in unmatched status on central matching utility. Internal confirmation for {trade_type} in {isin} with {cparty} was dispatched on trade date, but counterparty has submitted no matching instruction or allegement. Multiple automated chasers have elicited no response.",
            f"Zero allegement exception on order {trade_ref} at {csd}. Internal settlement instruction for {qty:,} shares of {isin} against {amount_str} was released to the utility, but counterparty {cparty} has not entered a corresponding instruction.",
            f"Matching utility reported status 'UNMATCHED - NO OPPOSING ADVICE' on ticket {trade_ref}. Trade with {cparty} for {isin} is approaching settlement deadline without counterparty confirmation.",
            f"Depository instruction unmatched for order {trade_ref}. Our delivery instruction was released on trade date, but counterparty {cparty} has not instructed their receiving agent bank at {csd}.",
            f"Awaiting counterparty affirmation on ticket {trade_ref}. Central matching utility indicates that while our trade details are affirmed, counterparty {cparty} has zero matching instructions logged."
        ]
        evidence = f"Counterparty {cparty} has submitted zero matching instructions or allegements on central utility for {trade_ref}."

    elif fam_idx == 2:
        # Theme: Counterparty states trade missing from internal blotter
        templates = [
            f"Electronic matching alert: Unconfirmed trade {trade_ref} with {cparty} for {qty:,} shares of {isin}. Counterparty operations desk states they have no record of this execution on their blotter. Front office has been requested to provide dealer recap chat transcripts.",
            f"Trade denial exception on ticket {trade_ref} in {isin}. Our back office issued confirmation for {amount_str}, but settlement operations at {cparty} denies knowledge of the executed trade.",
            f"Missing blotter entry on order {trade_ref}. Dealer recap indicates trade agreed with {cparty}, but counterpart middle office confirmed trade ticket was never entered into their capture system.",
            f"Unrecognised trade ticket exception on trade {trade_ref}. Settlement desk at {cparty} replied to inquiry stating transaction in {isin} does not appear on their internal ledger.",
            f"Bilateral booking dispute on order {trade_ref}. Our systems show confirmed purchase of {qty:,} units of {isin} from {cparty}, but counterparty insists no execution occurred."
        ]
        evidence = f"Counterparty {cparty} denies trade execution; transaction missing from counterparty internal blotter on {trade_ref}."

    elif fam_idx == 3:
        # Theme: Prime broker give-up unconfirmed / pending affirmation
        templates = [
            f"Matching utility reported status 'ALLEGED BY US - NO RECOGNITION' on {trade_ref}. Trade ticket details for {amount_str} against {isin} were sent to {cparty}, but counterpart clearing broker claims trade was executed via prime broker give-up and has not been affirmed by the end-client.",
            f"Prime broker give-up affirmation pending on ticket {trade_ref}. Executing broker {cparty} executed trade in {isin}, but designated prime broker has not accepted the give-up allocation at {csd}.",
            f"Give-up rejection alert on order {trade_ref} with {cparty}. Clearing broker refuses to instruct matching leg for {amount_str} until formal electronic affirmation is completed by underlying fund.",
            f"Unconfirmed give-up transaction on ticket {trade_ref} in {isin}. Trade remains stalled at {csd} because prime broker has not validated execution parameters with executing broker {cparty}.",
            f"Allocation give-up deadlock on trade {trade_ref}. Our delivery of {qty:,} shares of {isin} to {cparty} cannot match because counterparty clearing entity has not confirmed give-up acceptance."
        ]
        evidence = f"Prime broker give-up unconfirmed: executing broker {cparty} trade has not been affirmed by clearing entity on {trade_ref}."

    elif fam_idx == 4:
        # Theme: Counterparty claims trade cancelled prior to close
        templates = [
            f"Discrepancy in counterparty trade status on {trade_ref}. Our records show confirmed execution of {trade_type} with {cparty} in {isin}, but counterparty settlement desk claims trade was cancelled prior to market close. No bilateral cancellation ticket exists on our internal order management system.",
            f"Cancellation status dispute on order {trade_ref} at {csd}. Back office instructed delivery of {qty:,} shares of {isin} for {amount_str}, but counterparty {cparty} asserts transaction was voided by trading desk.",
            f"Conflicting trade status on ticket {trade_ref} with {cparty}. Internal systems treat trade in {isin} as live and deliverable, while counterparty flagged ticket as cancelled on their blotter.",
            f"Bilateral cancellation disagreement on order {trade_ref}. Counterparty {cparty} deleted matching instruction at {csd}, claiming verbal cancellation, whereas our trading desk confirms trade remains valid.",
            f"Unmatched trade conflict on ticket {trade_ref}. Our delivery instruction for {amount_str} remains open at {csd}, but counterparty {cparty} refuses to match, claiming trade was terminated."
        ]
        evidence = f"Trade cancellation dispute: counterparty {cparty} claims trade was cancelled without bilateral cancellation record on {trade_ref}."

    elif fam_idx == 5:
        # Theme: Inverted trade direction (both booked as Buy or both as Sell)
        templates = [
            f"Trade direction conflict on matching utility for ticket {trade_ref} with {cparty}. Internal booking records buy of {qty:,} shares of {isin}, but counterparty's incoming allegement also specifies a buy transaction. Both parties instructed receive-versus-payment at {csd}.",
            f"Inverted trade direction exception on order {trade_ref} in {isin}. Central matching utility flagged error because both our desk and counterparty {cparty} instructed delivery of securities rather than opposing delivery and receipt.",
            f"Matching engine rejection on trade {trade_ref}. Directional discrepancy detected: internal ticket indicates receive of {qty:,} shares of {isin}, while counterparty {cparty} also instructed receive.",
            f"Transaction side mismatch on ticket {trade_ref} with {cparty}. Trade for {amount_str} at {csd} cannot match because both bilateral instructions were submitted with Buy direction code.",
            f"Opposing leg conflict on order {trade_ref} in {isin}. Clearing agent at {csd} rejected settlement pairing because both internal operations and {cparty} submitted deliver instructions."
        ]
        evidence = f"Inverted trade direction: both internal desk and counterparty {cparty} instructed identical side (Buy/Buy or Sell/Sell) on {trade_ref}."

    elif fam_idx == 6:
        # Theme: Counterparty agent bank uninstructed
        templates = [
            f"Counterparty agent bank uninstructed on ticket {trade_ref} at {csd}. While {cparty}'s middle office confirmed trade agreement for {isin}, their appointed custody clearing agent has not submitted settlement instruction to the depository.",
            f"Sub-custodian instruction delay on order {trade_ref} with {cparty}. Our instruction for {amount_str} was validated at {csd}, but counterparty's settlement bank reports zero instruction received from {cparty}.",
            f"Depository queue hold on trade {trade_ref} in {isin}. Custodian {csd} confirmed our instruction is ready for matching, but counterparty agent bank has not received settlement authorization from {cparty}.",
            f"Missing agent instruction on ticket {trade_ref}. Front-office confirmed trade recap of {qty:,} shares with {cparty}, but counterpart clearing agent at {csd} has not released matching message.",
            f"Settlement pairing failure on order {trade_ref}. Counterparty {cparty} failed to dispatch instruction to their custodian at {csd}, leaving our settlement instruction in unmatched queue."
        ]
        evidence = f"Counterparty agent bank uninstructed: {cparty} failed to dispatch settlement authorization to depository agent on {trade_ref}."

    else:
        # Theme: Institutional master agreement bilateral confirmation missing
        templates = [
            f"Master confirmation agreement exception on ticket {trade_ref} with {cparty}. Over-the-counter transaction in {isin} for {amount_str} cannot settle because counterparty has not executed electronic master trade confirmation recap.",
            f"Bilateral confirmation hold on order {trade_ref} at {csd}. Internal operations placed trade on hold pending receipt of countersigned trade confirmation letter from {cparty}.",
            f"Confirmation recap missing on trade {trade_ref} in {isin}. Counterparty operations desk has not affirmed bilateral deal slip for {qty:,} shares, blocking instruction release to {csd}.",
            f"Unconfirmed deal recap on ticket {trade_ref} with {cparty}. Back office requires electronic affirmation of transaction terms before clearing instruction can pair at {csd}.",
            f"Bilateral affirmation deadlock on order {trade_ref}. Trade for {amount_str} in {isin} is stalled because counterparty {cparty} has not returned signed trade recap."
        ]
        evidence = f"Master bilateral trade confirmation recap unreturned/unaffirmed by counterparty {cparty} on {trade_ref}."

    return templates[var_idx % len(templates)], evidence


def _generate_settlement_timing_narrative(fam_idx: int, var_idx: int, cparty: str, curr: str, csd: str, trade_type: str, isin: str, qty: int, amount_str: str, trade_ref: str, rng: random.Random) -> Tuple[str, str]:
    """Generates distinct, diverse Settlement Timing narratives across 7 scenario families."""
    procedures = "PROC_11|PROC_12"

    if fam_idx == 1:
        # Theme: Settlement cycle discrepancy (T+1 vs T+2)
        templates = [
            f"Settlement date discrepancy on {trade_type} {trade_ref} with {cparty} in {isin}. Our ticket specifies settlement on T+1 under revised market rules, but counterparty instructed settlement on T+2. Depository {csd} rejected paired instruction due to mismatched intended settlement date (ISD).",
            f"Intended settlement date (ISD) mismatch on ticket {trade_ref}. Internal operations instructed settlement on T+1 for {amount_str}, but counterparty {cparty} submitted instruction for T+2 at {csd}. Transaction failed central matching.",
            f"Settlement cycle conflict on order {trade_ref} with {cparty}. Our back office booked {qty:,} shares of {isin} for next-day value date, while broker {cparty} confirmed trade on standard two-day settlement cycle.",
            f"Value date mismatch alert at {csd} on trade {trade_ref}. Paired settlement instructions failed auto-match because internal booking cites T+1 while counterparty {cparty} cites T+2 for {isin}.",
            f"Contractual settlement date disagreement on ticket {trade_ref}. Trade with {cparty} for {amount_str} cannot pair at {csd} due to conflicting intended settlement dates."
        ]
        evidence = f"Settlement cycle discrepancy: internal instruction booked on T+1 vs counterparty {cparty} instructed on T+2 on {trade_ref}."

    elif fam_idx == 2:
        # Theme: Late instruction release past RTGS depository cutoff
        templates = [
            f"Instruction failed market cutoff at {csd} for {trade_ref}. Settlement instructions for {isin} were released into depository queue at 17:15 local time, which is 15 minutes past real-time gross settlement cutoff for {curr}. Trade cannot settle today and must roll to next business day.",
            f"Depository cutoff deadline exceeded on ticket {trade_ref} with {cparty}. Delivery instruction for {amount_str} was received by {csd} after the mandatory 16:00 settlement cutoff, causing automatic roll.",
            f"Late release exception on order {trade_ref} in {isin}. Internal dispatch queue delay caused settlement message to reach {csd} past the same-day settlement input deadline for {curr}.",
            f"Cutoff violation alert at {csd} on trade {trade_ref}. Counterparty {cparty} matched in the utility, but our instruction arrived after the market cutoff for against-payment settlement.",
            f"Market deadline expired on order {trade_ref} for {qty:,} shares of {isin}. Instruction was rejected by clearing house {csd} due to submission past daily processing cutoff."
        ]
        evidence = f"Instruction submitted past depository market cutoff time at {csd} for {curr} on {trade_ref}."

    elif fam_idx == 3:
        # Theme: Local bank holiday / market calendar closure
        templates = [
            f"Market calendar conflict on trade {trade_ref} with {cparty}. Internal booking designated settlement date for {isin} falling on a local national bank holiday in the settlement jurisdiction. The local clearing house {csd} was closed, causing automated settlement engine rejection.",
            f"Bank holiday settlement rejection on ticket {trade_ref} for {amount_str}. Settlement was instructed for a date when local central bank payment clearing was closed for holiday, preventing cash wire settlement with {cparty}.",
            f"Exchange holiday closure exception on order {trade_ref} in {isin}. Our back office instructed settlement date during national holiday in market jurisdiction, causing depository {csd} to reject instruction.",
            f"Non-clearing day conflict on trade {trade_ref} with {cparty}. Intended value date falls on regional banking holiday, requiring settlement date amendment to next mutual business day.",
            f"Holiday calendar misalignment on ticket {trade_ref}. Depository {csd} rejected settlement of {qty:,} shares of {isin} because designated settlement date is an official market holiday in {curr} clearing."
        ]
        evidence = f"Market calendar closure: intended settlement date coincides with bank holiday in {csd} jurisdiction on {trade_ref}."

    elif fam_idx == 4:
        # Theme: Extended settlement date verbal agreement vs standard dispatch
        templates = [
            f"Timing misalignment on cross-border delivery {trade_ref} for {isin}. Trade execution agreed on extended settlement date (T+5), but internal automated dispatch pushed instruction for standard T+1 settlement. Counterparty {cparty} instructed for agreed extended value date, creating ISD mismatch in matching engine.",
            f"Extended value date conflict on order {trade_ref} with {cparty}. Trading desk negotiated special extended settlement for {amount_str}, but settlement system defaulted to standard cycle, causing pairing rejection at {csd}.",
            f"Special settlement terms disagreement on ticket {trade_ref} in {isin}. Counterparty {cparty} instructed extended settlement on Friday, whereas internal instruction released for Thursday.",
            f"Settlement date scheduling error on order {trade_ref}. Back office omitted extended settlement flag for {qty:,} units of {isin}, causing ISD mismatch against {cparty} at {csd}.",
            f"Non-standard settlement cycle exception on ticket {trade_ref}. Trader recap agreed extended settlement date with {cparty}, but automated gateway transmitted standard value date to {csd}."
        ]
        evidence = f"Extended settlement terms mismatch: internal dispatch pushed standard cycle while counterparty {cparty} instructed extended date on {trade_ref}."

    elif fam_idx == 5:
        # Theme: Internal batch processing queue latency
        templates = [
            f"Cutoff window violation: Batch release delay in internal operations queue prevented transmission of settlement instruction {trade_ref} to {csd} before the mandatory 14:00 cutoff. Counterparty {cparty} matched in utility, but late internal release prevented same-day execution.",
            f"Internal batch processing latency on ticket {trade_ref} for {isin}. System batch job backlog delayed generation of SWIFT MT541 instruction until after depository matching cutoff at {csd}.",
            f"Queue latency exception on order {trade_ref} with {cparty}. Trade was approved on time, but messaging bridge latency held transmission of {amount_str} past clearing cutoff.",
            f"Operations batch delay on trade {trade_ref} in {isin}. Settlement message reached {csd} late due to internal gateway synchronization lag, causing trade to fail same-day cycle.",
            f"Late dispatch queue alert on ticket {trade_ref}. Internal overnight batch delay prevented timely transmission of instruction for {qty:,} shares of {isin} to counterparty clearing agent."
        ]
        evidence = f"Internal batch queue latency: technical dispatch backlog caused late transmission past depository cutoff at {csd} on {trade_ref}."

    elif fam_idx == 6:
        # Theme: Cross-border time zone disparity in Asian/European clearing
        templates = [
            f"Time zone clearing window disparity on cross-border trade {trade_ref} with {cparty}. Trade in {isin} required early morning Tokyo/Hong Kong settlement, but instruction was transmitted during London business hours, missing Asian clearing cycle at {csd}.",
            f"Asian clearing cutoff missed on ticket {trade_ref} for {amount_str}. Counterparty {cparty} instructed for same-day settlement in Asian time zone, but internal operations dispatched after local market cutoff.",
            f"Cross-border time zone conflict on order {trade_ref} in {isin}. International trade with {cparty} failed because time zone lag between counterparties prevented timely matching before regional depository close.",
            f"Regional operating timetable exception on trade {trade_ref}. Settlement instruction for {qty:,} shares was entered too late to meet early morning market cutoff in destination clearing jurisdiction.",
            f"Time zone matching deadlock on ticket {trade_ref} with {cparty}. Bilateral matching window closed before counterparty instruction could pair at overseas central depository."
        ]
        evidence = f"Time zone disparity: instruction dispatched past overseas regional market cutoff at {csd} on {trade_ref}."

    else:
        # Theme: Non-business day weekend value date roll dispute
        templates = [
            f"Value date weekend roll conflict on ticket {trade_ref} with {cparty}. Internal booking adjusted trade value date to Monday following Saturday execution, while counterparty {cparty} instructed value date for Friday. Depository {csd} rejected mismatched ISD.",
            f"Non-business day settlement error on order {trade_ref} in {isin}. Instruction was booked with intended settlement date falling on a Sunday, causing automated validation rejection at {csd}.",
            f"Weekend value date dispute on trade {trade_ref} for {amount_str}. Counterparty {cparty} rolled trade date to next business day, while internal system rolled settlement date, causing pairing failure.",
            f"Calendar roll exception on ticket {trade_ref} with {cparty}. Bilateral instructions disagree by one business day following weekend trade date adjustment at {csd}.",
            f"Business day convention conflict on order {trade_ref} in {isin}. Back office applied modified following business day rule, while broker {cparty} instructed following business day rule."
        ]
        evidence = f"Business day convention / weekend value date roll discrepancy between internal booking and counterparty {cparty} on {trade_ref}."

    return templates[var_idx % len(templates)], evidence


def generate_scenario_variants(
    category: str,
    family_idx: int,
    variant_idx: int,
    rng: random.Random
) -> Dict[str, Any]:
    """Generate a single diverse case based on category and scenario family."""
    cparty = rng.choice(COUNTERPARTIES)
    curr = rng.choice(CURRENCIES)
    csd = rng.choice(DEPOSITORIES)
    trade_type = rng.choice(TRADE_TYPES)
    status = rng.choice(STATUSES)
    isin_prefix = rng.choice(["US", "GB", "DE", "FR", "CH", "XS", "JP", "CA"])
    isin_suffix = f"{rng.randint(100000000, 999999999)}"
    isin = f"{isin_prefix}{isin_suffix}"
    qty = rng.choice([2500, 10000, 45000, 125000, 500000, 1200000])
    amount = round(qty * rng.uniform(12.5, 420.0), 2)
    amount_str = f"{amount:,.2f} {curr}"
    trade_ref = f"TRD-{category[:3]}-{family_idx:02d}-{variant_idx:02d}-{rng.randint(1000, 9999)}"
    family_id = f"FAM-{category[:3]}-{family_idx:02d}"

    if category == "SSI_MISMATCH":
        procedures = "PROC_01|PROC_02"
        desc, evidence = _generate_ssi_narrative(family_idx, variant_idx, cparty, curr, csd, trade_type, isin, qty, amount_str, trade_ref, rng)

    elif category == "TRADE_DETAIL_MISMATCH":
        procedures = "PROC_03|PROC_04"
        desc, evidence = _generate_trade_detail_narrative(family_idx, variant_idx, cparty, curr, csd, trade_type, isin, qty, amount, amount_str, trade_ref, rng)

    elif category == "SECURITIES_SHORTFALL":
        procedures = "PROC_05|PROC_06"
        desc, evidence = _generate_securities_shortfall_narrative(family_idx, variant_idx, cparty, curr, csd, trade_type, isin, qty, amount_str, trade_ref, rng)

    elif category == "CASH_SHORTFALL":
        procedures = "PROC_07|PROC_08"
        desc, evidence = _generate_cash_shortfall_narrative(family_idx, variant_idx, cparty, curr, csd, trade_type, isin, qty, amount, amount_str, trade_ref, rng)

    elif category == "COUNTERPARTY_UNCONFIRMED":
        procedures = "PROC_09|PROC_10"
        desc, evidence = _generate_counterparty_unconfirmed_narrative(family_idx, variant_idx, cparty, curr, csd, trade_type, isin, qty, amount_str, trade_ref, rng)

    elif category == "SETTLEMENT_TIMING":
        procedures = "PROC_11|PROC_12"
        desc, evidence = _generate_settlement_timing_narrative(family_idx, variant_idx, cparty, curr, csd, trade_type, isin, qty, amount_str, trade_ref, rng)

    return {
        "scenario_family_id": family_id,
        "case_description": desc,
        "trade_type": trade_type,
        "transaction_status": status,
        "exception_code": f"EXC_{category[:4]}_{rng.randint(100, 999)}",
        "expected_category": category,
        "ground_truth_evidence": evidence,
        "relevant_procedure_ids": procedures,
        "is_sufficiently_informative": True,
    }


def generate_ambiguous_case(
    case_idx: int,
    rng: random.Random
) -> Dict[str, Any]:
    """Generate an ambiguous case with insufficient, contradictory, or truncated details."""
    cparty = rng.choice(COUNTERPARTIES)
    isin_prefix = rng.choice(["US", "GB", "DE", "FR", "XS", "CH", "NL"])
    isin = f"{isin_prefix}{rng.randint(100000000, 999999999)}"
    csd = rng.choice(DEPOSITORIES)
    family_id = f"FAM-AMB-{(case_idx // 5) + 1:02d}"
    ref = f"AMB-{case_idx + 1:03d}-{rng.randint(1000, 9999)}"
    trade_type_choice = rng.choice(TRADE_TYPES)

    ambiguous_templates = [
        f"Settlement failure notification received from {csd} for trade {ref} with {cparty}. Status indicates 'FAIL - UNKNOWN REASON'. The message text is truncated and contains no error sub-codes, counterparty account details, or diagnostic information.",
        f"Transaction {ref} for {isin} remains in pending exception queue. Front-office trade support notes an apparent operational breakdown, but available logs show both a pending cash transfer and an unconfirmed allocation ticket from {cparty}. Data is insufficient to determine the root cause.",
        f"Exception reported on trade {ref} with {cparty}. System audit log contains contradictory alerts: depository flags possible cutoff deadline issue while matching utility simultaneously flags mismatched settlement instructions. No source documents are attached.",
        f"Trade status for {isin} under ticket {ref} shows 'SUSPENDED'. No narrative explanation or error code was populated by the gateway. The transaction details list counterparty {cparty}, but settlement accounts and consideration amounts are blank.",
        f"Bilateral communication log for {ref} indicates a dispute with {cparty} regarding trade in {isin}, but correspondence is ambiguous as to whether the issue relates to price recalculation or unexpected settlement date roll over the holiday weekend.",
        f"Settlement failed during overnight processing batch at {csd} for ticket {ref}. The automated report lists error code 'SYS_ERR_GENERIC' without specifying whether the failure was caused by inventory deficit, cash shortage, or depository technical error.",
        f"Trade {ref} in {isin} with {cparty} failed validation. Diagnostic string reads: 'Error 999: Unclassified processing exception; contact clearing desk'. All economic fields appear populated but no matching or clearing logs were returned.",
        f"Operations incident record {ref}: Exception flagged on cross-border transaction with {cparty}. Ledger reports pending settlement, but counterparty email mentions both an instruction query and a holiday cutoff question with conflicting timestamps.",
        f"Audit trail for settlement instruction {ref} at {csd} is incomplete. Status transitioned from PENDING to FAILED at 18:00 without reason codes. Neither cash debit nor inventory reservation entries were logged in the sub-custody feed.",
        f"Discrepancy notice {ref} received from broker {cparty} regarding {isin}. Text notes: 'Trade unaligned with internal expectation'. Specifics regarding whether the mismatch is in quantity, price, or settlement agent are entirely missing from the memo.",
        f"Exception ticket {ref} logged for {trade_type_choice}. Central matching service indicates a status of 'HOLD' without secondary qualifier codes. Correspondence between operations desks ended abruptly without field reconciliation.",
        f"Settlement alert {ref} for {cparty}: Clearing gateway returned an unformatted text string 'ERR_COMM_TIMEOUT_CSD'. It is unresolved whether instructions reached {csd} or if trade details failed pre-settlement format checks.",
        f"Reconciliation queue for {ref} displays conflicting trade attributes across two front-office systems. System A reports trade settled, whereas System B reports trade rejected by counterparty {cparty} with no detailed error message attached.",
        f"Trade {ref} in {isin} reported as 'SUSPENDED - PENDING INVESTIGATION' by clearing agent. Narrative contains partial notes: 'Checking with local market agent regarding potential issue...' No further operational update provided.",
        f"Unresolved exception record {ref}: Ticket was flagged by automated reconciliation monitor. Description says 'Unmatched or unconfirmed trade leg', but attached snapshot shows matching confirmation timestamp without counterparty confirmation details.",
        f"Depository advice for {ref} notes 'TRANSACTION BLOCKED'. Error field lists code 'ERR_MISC_DATA'. Neither internal back office nor broker {cparty} has identified which field is invalid.",
        f"Investigation ticket {ref} for {trade_type_choice}: Gateway received partial cancellation request from {cparty}, but trade status at {csd} displays 'PENDING_SETTLEMENT'. No explanation attached.",
        f"Operations inquiry {ref}: Cross-border settlement in {isin} stalled. Counterparty {cparty} sent message stating 'Please investigate trade differences', without attaching allocation breakdown or discrepancy codes.",
        f"Exception notice {ref} at {csd}: Transaction failed overnight matching cycle. Reason code is missing, and audit logs do not clarify whether counterparty failed to affirm or instructed different consideration.",
        f"Settlement monitor alert {ref}: Status for {cparty} is 'EXCEPTION_UNSPECIFIED'. Trade date, settlement date, and amount are recorded, but failure reason was overwritten by system timeout error.",
        f"Reconciliation alert {ref}: Trade in {isin} shows contradictory status flags: 'MATCHED_PENDING' on utility but 'REJECTED_CSD' on custody report. Field differences are not identified.",
        f"Depository notification {ref}: Instruction for {cparty} failed validation with generic code 'NACK_000'. Notes indicate 'Contact depository representative for error breakdown'.",
        f"Broker correspondence for {ref} shows ongoing disagreement regarding trade in {isin}, but correspondence fragments conflict between a settlement date query and an account number confirmation.",
        f"Settlement log {ref} for {trade_type_choice}: Status is 'ON_HOLD'. The audit memo states 'Review required by operations manager' without identifying underlying transactional discrepancy.",
        f"Gateway error {ref}: Clearing message for {isin} with {cparty} was rejected with error text 'PAYLOAD_TRUNCATED'. Source document details are unavailable.",
        f"Exception report {ref}: Trade with {cparty} failed settlement batch. The narrative field reads: 'Refer to manual ticketing system', but corresponding record was not located in internal database.",
        f"Discrepancy record {ref} in {isin}: Counterparty {cparty} flagged trade with memo 'Under review', but matching utility fields show identical nominal values and dates.",
        f"Settlement exception ticket {ref}: Custodian reported error 'ERR_BATCH_ABORT' during processing of {trade_type_choice}. Individual trade details were not evaluated before batch failure.",
        f"Bilateral note for {ref}: Counterparty {cparty} claims trade in {isin} is subject to an operational dispute, but dispute documentation has not been submitted.",
        f"Unresolved exception {ref}: Transaction is stalled between custody and matching layers. Diagnostic logs are contradictory, showing both normal acknowledgement and a generic rejection code."
    ]

    desc = ambiguous_templates[case_idx % len(ambiguous_templates)]

    return {
        "scenario_family_id": family_id,
        "case_description": desc,
        "trade_type": trade_type_choice,
        "transaction_status": "SUSPENDED_UNSPECIFIED",
        "exception_code": f"EXC_AMB_{rng.randint(100, 999)}",
        "expected_category": AMBIGUOUS_LABEL,
        "ground_truth_evidence": f"Narrative provides incomplete, contradictory, or truncated evidence insufficient for definitive categorization on {ref}.",
        "relevant_procedure_ids": "PROC_13|PROC_14",
        "is_sufficiently_informative": False,
    }


def generate_full_dataset(seed: int = RANDOM_SEED) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, List[Dict[str, Any]]]:
    """
    Generates:
    - 210 labelled cases (35 per category across 6 categories, 7 families per category, 5 variants per family)
    - 30 ambiguous cases (6 families of 5)
    - Total: 240 cases
    Returns (all_df, labeled_df, ambiguous_df, sample_cases_list)
    """
    rng = random.Random(seed)
    all_cases: List[Dict[str, Any]] = []

    case_counter = 1

    # 1. Generate 210 labelled cases (35 per category)
    for cat in CANONICAL_CATEGORIES:
        for fam_idx in range(1, 8):  # 7 distinct scenario families per category
            for var_idx in range(5):  # 5 distinct variants per family
                case_data = generate_scenario_variants(cat, fam_idx, var_idx, rng)
                case_data["case_id"] = f"SS-{case_counter:04d}"
                all_cases.append(case_data)
                case_counter += 1

    # 2. Generate 30 ambiguous cases
    ambiguous_cases: List[Dict[str, Any]] = []
    for amb_idx in range(30):
        case_data = generate_ambiguous_case(amb_idx, rng)
        case_data["case_id"] = f"SS-{case_counter:04d}"
        all_cases.append(case_data)
        ambiguous_cases.append(case_data)
        case_counter += 1

    all_df = pd.DataFrame(all_cases)
    labeled_df = all_df[all_df["is_sufficiently_informative"] == True].copy()
    ambiguous_df = all_df[all_df["is_sufficiently_informative"] == False].copy()

    # Create representative sample cases for Streamlit UI dropdown
    sample_cases = []
    for cat in CANONICAL_CATEGORIES:
        cat_sample = labeled_df[labeled_df["expected_category"] == cat].iloc[0].to_dict()
        sample_cases.append({
            "case_id": cat_sample["case_id"],
            "expected_category": cat_sample["expected_category"],
            "label_preview": f"[{cat}] {cat_sample['case_id']}: {cat_sample['trade_type']}",
            "case_description": cat_sample["case_description"],
            "trade_type": cat_sample["trade_type"],
            "transaction_status": cat_sample["transaction_status"],
            "exception_code": cat_sample["exception_code"],
        })

    for i in range(2):
        amb_sample = ambiguous_df.iloc[i].to_dict()
        sample_cases.append({
            "case_id": amb_sample["case_id"],
            "expected_category": amb_sample["expected_category"],
            "label_preview": f"[UNDETERMINED] {amb_sample['case_id']}: Incomplete / Ambiguous Case",
            "case_description": amb_sample["case_description"],
            "trade_type": amb_sample["trade_type"],
            "transaction_status": amb_sample["transaction_status"],
            "exception_code": amb_sample["exception_code"],
        })

    return all_df, labeled_df, ambiguous_df, sample_cases


def save_dataset(output_dir: Path = DATA_DIR, seed: int = RANDOM_SEED) -> Dict[str, Path]:
    """Generates and writes CSVs and sample JSON to output directory."""
    all_df, labeled_df, ambiguous_df, sample_cases = generate_full_dataset(seed)

    output_dir.mkdir(parents=True, exist_ok=True)

    settlement_cases_path = output_dir / "settlement_cases.csv"
    labeled_cases_path = output_dir / "labeled_cases.csv"
    ambiguous_cases_path = output_dir / "ambiguous_cases.csv"
    sample_cases_path = output_dir / "sample_cases.json"

    all_df.to_csv(settlement_cases_path, index=False)
    labeled_df.to_csv(labeled_cases_path, index=False)
    ambiguous_df.to_csv(ambiguous_cases_path, index=False)

    with open(sample_cases_path, "w", encoding="utf-8") as f:
        json.dump(sample_cases, f, indent=2)

    return {
        "settlement_cases": settlement_cases_path,
        "labeled_cases": labeled_cases_path,
        "ambiguous_cases": ambiguous_cases_path,
        "sample_cases": sample_cases_path,
    }

if __name__ == "__main__":
    paths = save_dataset()
    print("Dataset generation complete:")
    for k, v in paths.items():
        print(f"  - {k}: {v}")
