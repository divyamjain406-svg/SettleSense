"""
Unit tests for Approach A: TF-IDF + Logistic Regression classifier.
"""

import pytest
from config.settings import CANONICAL_CATEGORIES
from src.train_classifier import prepare_data, train_and_evaluate, SettlementClassifier

def test_prepare_data_split_integrity():
    """Verify that train and test scenario families do not overlap."""
    train_df, test_df = prepare_data()
    train_families = set(train_df["scenario_family_id"].unique())
    test_families = set(test_df["scenario_family_id"].unique())
    overlap = train_families.intersection(test_families)
    assert len(overlap) == 0, f"Scenario family leakage found: {overlap}"
    assert len(train_df) > 0
    assert len(test_df) > 0

def test_classifier_training_metrics():
    """Verify classifier trains and produces valid metrics within expected performance bounds."""
    train_df, test_df = prepare_data()
    clf, vectorizer, metrics, pred_df = train_and_evaluate(train_df, test_df)

    assert metrics["accuracy"] >= 0.85, f"Accuracy too low: {metrics['accuracy']}"
    assert metrics["macro_f1"] >= 0.85, f"Macro F1 too low: {metrics['macro_f1']}"
    assert len(pred_df) == len(test_df)
    assert "predicted_category" in pred_df.columns

def test_settlement_classifier_inference():
    """Verify SettlementClassifier wrapper inference on unseen narratives."""
    classifier = SettlementClassifier()
    assert classifier.is_ready, "Classifier should be loaded and ready"

    # Test cash shortfall narrative
    cash_query = "Cash clearing agent reported settlement failure due to insufficient available Nostro balance"
    pred = classifier.predict(cash_query)
    assert pred["predicted_category"] == "CASH_SHORTFALL"
    assert pred["confidence"] > 0.3
    assert set(pred["probabilities"].keys()) == set(CANONICAL_CATEGORIES)

    # Test SSI mismatch narrative
    ssi_query = "Depository notification reported settlement rejection because safekeeping account differed from counterparty standing instructions"
    pred_ssi = classifier.predict(ssi_query)
    assert pred_ssi["predicted_category"] == "SSI_MISMATCH"

    # Test empty input handling
    pred_empty = classifier.predict("")
    assert pred_empty["predicted_category"] == "UNDETERMINED"
    assert pred_empty["confidence"] == 0.0

