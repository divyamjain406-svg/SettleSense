"""
Data validation module for SettleSense.
Performs verification of schemas, label spaces, duplicate identifiers,
near-duplicate narratives, scenario-family integrity, and target label leakage.
"""

from typing import Dict, Any, List, Set, Tuple
import pandas as pd
from config.settings import CANONICAL_CATEGORIES, AMBIGUOUS_LABEL, ALL_LABELS

REQUIRED_COLUMNS = [
    "case_id",
    "scenario_family_id",
    "case_description",
    "trade_type",
    "transaction_status",
    "exception_code",
    "expected_category",
    "ground_truth_evidence",
    "relevant_procedure_ids",
    "is_sufficiently_informative",
]

def validate_dataset_schema(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Checks that all required columns are present in the DataFrame."""
    errors = []
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")
    return len(errors) == 0, errors


def validate_labels(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Checks that all expected_category values belong to allowed label set."""
    errors = []
    invalid_labels = df[~df["expected_category"].isin(ALL_LABELS)]["expected_category"].unique().tolist()
    if invalid_labels:
        errors.append(f"Invalid category labels found: {invalid_labels}")
    return len(errors) == 0, errors


def validate_counts(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validates dataset row counts:
    - Exactly 35 cases per canonical category
    - Exactly 30 cases for UNDETERMINED
    - Total 240 cases
    """
    errors = []
    if len(df) != 240:
        errors.append(f"Expected 240 total cases, but got {len(df)}")

    cat_counts = df["expected_category"].value_counts().to_dict()
    for cat in CANONICAL_CATEGORIES:
        count = cat_counts.get(cat, 0)
        if count != 35:
            errors.append(f"Expected 35 cases for category '{cat}', got {count}")

    amb_count = cat_counts.get(AMBIGUOUS_LABEL, 0)
    if amb_count != 30:
        errors.append(f"Expected 30 cases for ambiguous category '{AMBIGUOUS_LABEL}', got {amb_count}")

    informative_counts = df["is_sufficiently_informative"].value_counts().to_dict()
    if informative_counts.get(True, 0) != 210:
        errors.append(f"Expected 210 informative cases, got {informative_counts.get(True, 0)}")
    if informative_counts.get(False, 0) != 30:
        errors.append(f"Expected 30 uninformative cases, got {informative_counts.get(False, 0)}")

    return len(errors) == 0, errors


def validate_uniqueness_and_nulls(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Verifies no duplicate case IDs and no missing/null values in required fields."""
    errors = []
    dup_ids = df[df.duplicated(subset=["case_id"])]["case_id"].tolist()
    if dup_ids:
        errors.append(f"Duplicate case_id values found: {dup_ids}")

    null_counts = df[REQUIRED_COLUMNS].isnull().sum()
    cols_with_nulls = null_counts[null_counts > 0].to_dict()
    if cols_with_nulls:
        errors.append(f"Columns with null values detected: {cols_with_nulls}")

    # Check for identical duplicate narratives
    dup_narratives = df[df.duplicated(subset=["case_description"])]["case_id"].tolist()
    if dup_narratives:
        errors.append(f"Exact duplicate narratives found in cases: {dup_narratives}")

    return len(errors) == 0, errors


def validate_target_leakage(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Checks that the target category name does not verbatim appear in the case description
    or in identifiers (e.g. case_id does not contain SSI_MISMATCH).
    """
    errors = []
    for idx, row in df.iterrows():
        case_id = str(row["case_id"])
        cat = str(row["expected_category"])
        desc = str(row["case_description"]).lower()

        # Identifier check
        if cat.lower() in case_id.lower():
            errors.append(f"Case {case_id}: Target category '{cat}' leaked into case_id")

        # Verbatim category name leakage in description
        cat_tokens = cat.lower().replace("_", " ")
        if cat_tokens in desc:
            errors.append(f"Case {case_id}: Target category phrase '{cat_tokens}' explicitly leaked into narrative")

    return len(errors) == 0, errors


def validate_split_integrity(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame
) -> Tuple[bool, List[str]]:
    """
    Verifies scenario-family split integrity:
    No scenario_family_id should appear in both train and test partitions.
    """
    errors = []
    train_families: Set[str] = set(train_df["scenario_family_id"].unique())
    test_families: Set[str] = set(test_df["scenario_family_id"].unique())
    overlap = train_families.intersection(test_families)
    if overlap:
        errors.append(f"Data leakage detected! Scenario families present in both train and test: {overlap}")
    return len(errors) == 0, errors


def run_all_dataset_validations(df: pd.DataFrame) -> Dict[str, Any]:
    """Runs the complete battery of validations on a dataset DataFrame."""
    results = {}
    validations = [
        ("schema", validate_dataset_schema),
        ("labels", validate_labels),
        ("counts", validate_counts),
        ("uniqueness_and_nulls", validate_uniqueness_and_nulls),
        ("target_leakage", validate_target_leakage),
    ]

    all_passed = True
    collected_errors = []

    for name, val_func in validations:
        passed, errors = val_func(df)
        results[name] = {"passed": passed, "errors": errors}
        if not passed:
            all_passed = False
            collected_errors.extend(errors)

    results["overall_passed"] = all_passed
    results["all_errors"] = collected_errors
    return results

