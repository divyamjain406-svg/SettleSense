"""
Pydantic schemas for SettleSense structured investigation reports.
Enforces validation rules, allowed categories, and required investigation fields.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator

# Allowed failure categories including uncertainty
CandidateCategory = Literal[
    "SSI_MISMATCH",
    "TRADE_DETAIL_MISMATCH",
    "SECURITIES_SHORTFALL",
    "CASH_SHORTFALL",
    "COUNTERPARTY_UNCONFIRMED",
    "SETTLEMENT_TIMING",
    "UNDETERMINED",
]

ConfidenceLevel = Literal["HIGH", "MEDIUM", "LOW", "UNCERTAIN"]


class ProcedureCitation(BaseModel):
    """Structured citation metadata for an evidence reference."""
    procedure_id: str
    procedure_title: Optional[str] = None
    is_valid_id: bool = True


class SettlementInvestigationReport(BaseModel):
    """
    Structured Copilot Investigation Report Schema.
    Adheres strictly to financial operations investigation guardrails:
    - Distinguishes observed facts from possible causes.
    - Cites relevant procedure documents.
    - Flags cases requiring mandatory human review.
    """
    case_id: str = Field(
        ...,
        description="Unique identifier of the settlement exception case."
    )
    case_summary: str = Field(
        ...,
        description="Concise factual summary of the observed settlement exception."
    )
    candidate_failure_category: CandidateCategory = Field(
        ...,
        description="Preliminary candidate failure category or UNDETERMINED if evidence is insufficient."
    )
    category_confidence_or_uncertainty: ConfidenceLevel = Field(
        ...,
        description="Confidence assessment in the candidate categorization."
    )
    supporting_evidence: List[str] = Field(
        default_factory=list,
        description="Objective transactional facts extracted strictly from the case narrative."
    )
    possible_causes: List[str] = Field(
        default_factory=list,
        description="Plausible operational hypotheses explaining the exception (not unconfirmed root causes)."
    )
    recommended_checks: List[str] = Field(
        default_factory=list,
        description="Specific verification steps an operations analyst should execute."
    )
    missing_information: List[str] = Field(
        default_factory=list,
        description="Missing data fields or pending confirmations required for resolution."
    )
    procedure_references: List[str] = Field(
        default_factory=list,
        description="List of cited procedure IDs (e.g., ['PROC_01', 'PROC_02']) supporting the recommendations."
    )
    investigation_note: str = Field(
        ...,
        description="Professional operational guidance note summarizing risk and next steps."
    )
    requires_human_review: bool = Field(
        default=True,
        description="True if manual analyst review and confirmation is mandatory."
    )

    @field_validator("candidate_failure_category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        valid_cats = {
            "SSI_MISMATCH", "TRADE_DETAIL_MISMATCH", "SECURITIES_SHORTFALL",
            "CASH_SHORTFALL", "COUNTERPARTY_UNCONFIRMED", "SETTLEMENT_TIMING",
            "UNDETERMINED"
        }
        if v not in valid_cats:
            raise ValueError(f"Invalid category '{v}'. Must be one of {valid_cats}")
        return v

    @field_validator("requires_human_review")
    @classmethod
    def enforce_human_review_for_undetermined(cls, v: bool, info) -> bool:
        # If candidate category is UNDETERMINED or confidence is LOW/UNCERTAIN, enforce human review
        data = info.data
        if data.get("candidate_failure_category") == "UNDETERMINED":
            return True
        if data.get("category_confidence_or_uncertainty") in ["LOW", "UNCERTAIN"]:
            return True
        return v

