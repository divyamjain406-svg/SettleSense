"""
Unit tests for dataset schema, validation rules, determinism, and scenario-family integrity.
"""

import pandas as pd
import pytest
from config.settings import DATA_DIR, CANONICAL_CATEGORIES, AMBIGUOUS_LABEL
from src.data_generator import generate_full_dataset
from src.data_validation import (
    validate_dataset_schema,
    validate_labels,
    validate_counts,
    validate_uniqueness_and_nulls,
    validate_target_leakage,
    validate_split_integrity,
    run_all_dataset_validations,
)

def test_dataset_generation_determinism():
    """Verify that generating with seed 42 produces identical dataframes."""
    df1, _, _, _ = generate_full_dataset(seed=42)
    df2, _, _, _ = generate_full_dataset(seed=42)
    pd.testing.assert_frame_equal(df1, df2)

def test_dataset_schema():
    """Check that generated CSV has all required columns."""
    csv_path = DATA_DIR / "settlement_cases.csv"
    assert csv_path.exists(), "settlement_cases.csv should exist"
    df = pd.read_csv(csv_path)
    passed, errors = validate_dataset_schema(df)
    assert passed, f"Schema validation failed: {errors}"

def test_category_labels_and_counts():
    """Verify label validity and 35/30 distribution counts."""
    csv_path = DATA_DIR / "settlement_cases.csv"
    df = pd.read_csv(csv_path)
    
    passed_labels, err_labels = validate_labels(df)
    assert passed_labels, f"Labels invalid: {err_labels}"
    
    passed_counts, err_counts = validate_counts(df)
    assert passed_counts, f"Counts invalid: {err_counts}"

def test_uniqueness_and_no_nulls():
    """Verify unique case IDs and no missing fields."""
    csv_path = DATA_DIR / "settlement_cases.csv"
    df = pd.read_csv(csv_path)
    passed, errors = validate_uniqueness_and_nulls(df)
    assert passed, f"Uniqueness or null checks failed: {errors}"

def test_no_target_leakage_in_features():
    """Verify category names are not verbatim in case_description or case_id."""
    csv_path = DATA_DIR / "settlement_cases.csv"
    df = pd.read_csv(csv_path)
    passed, errors = validate_target_leakage(df)
    assert passed, f"Target leakage detected: {errors}"

def test_split_integrity_detector():
    """Test that validate_split_integrity detects leakage when scenario families overlap."""
    clean_train = pd.DataFrame({"scenario_family_id": ["FAM-01", "FAM-02"]})
    clean_test = pd.DataFrame({"scenario_family_id": ["FAM-03", "FAM-04"]})
    passed, errors = validate_split_integrity(clean_train, clean_test)
    assert passed
    assert len(errors) == 0

    leaky_test = pd.DataFrame({"scenario_family_id": ["FAM-02", "FAM-05"]})
    passed_leaky, errors_leaky = validate_split_integrity(clean_train, leaky_test)
    assert not passed_leaky
    assert len(errors_leaky) > 0
    assert "FAM-02" in errors_leaky[0]

