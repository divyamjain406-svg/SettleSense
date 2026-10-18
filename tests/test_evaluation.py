"""
Unit tests for evaluation metrics, retrieval calculations, and artifact verification.
"""

from pathlib import Path
import pandas as pd
from config.settings import RESULTS_DIR, FIGURES_DIR
from src.lexical_retrieval import evaluate_lexical_retrieval
from src.semantic_retrieval import evaluate_semantic_retrieval

def test_evaluation_metric_calculation_lexical():
    """Verify lexical retrieval evaluation returns valid metric values within [0.0, 1.0]."""
    metrics = evaluate_lexical_retrieval(top_k=3)
    assert "hit@3" in metrics
    assert "recall@3" in metrics
    assert "mrr" in metrics
    assert 0.0 <= metrics["hit@3"] <= 1.0
    assert 0.0 <= metrics["recall@3"] <= 1.0
    assert 0.0 <= metrics["mrr"] <= 1.0

from unittest.mock import patch

def test_evaluation_metric_calculation_semantic():
    """Verify semantic retrieval evaluation metric calculations with mocked retriever."""
    mock_results = [
        {"procedure_id": "PROC_01", "similarity_score": 0.85},
        {"procedure_id": "PROC_02", "similarity_score": 0.72},
        {"procedure_id": "PROC_03", "similarity_score": 0.60},
    ]
    with patch("src.semantic_retrieval.SemanticRetriever.retrieve", return_value=mock_results):
        metrics = evaluate_semantic_retrieval(top_k=3)
        assert "hit@3" in metrics
        assert "recall@3" in metrics
        assert "mrr" in metrics
        assert 0.0 <= metrics["hit@3"] <= 1.0
        assert 0.0 <= metrics["recall@3"] <= 1.0
        assert 0.0 <= metrics["mrr"] <= 1.0

def test_evaluation_artifacts_exist():
    """Verify that all required result CSVs and visualization figures were generated."""
    metrics_csv = RESULTS_DIR / "metrics.csv"
    comp_csv = RESULTS_DIR / "comparison_table.csv"
    assert metrics_csv.exists(), "results/metrics.csv must exist"
    assert comp_csv.exists(), "results/comparison_table.csv must exist"

    required_figures = [
        "class_distribution.png",
        "confusion_matrix.png",
        "macro_f1_comparison.png",
        "retrieval_hit3_comparison.png",
        "response_latency_comparison.png",
        "uncertainty_handling.png",
    ]
    for fig_name in required_figures:
        fig_path = FIGURES_DIR / fig_name
        assert fig_path.exists(), f"Figure {fig_name} must exist"
        assert fig_path.stat().st_size > 1000, f"Figure {fig_name} must not be empty"


from src.evaluation import extract_metric_value, format_kpi_value
import numpy as np

def test_extract_metric_value():
    """Verify robust extraction of numeric metrics with exact, case-insensitive, and prefix matching."""
    sample_metrics = {
        "Classifier Accuracy (Held-out Test Split)": "0.9455",
        "Classifier Macro-F1 (Held-out Test Split)": 0.9281,
        "Lexical Retrieval Hit@3 (Labelled Cases)": 0.9238,
        "Semantic Retrieval Hit@3 (Labelled Cases)": 0.9762,
        "Approach D Human-Reviewed Evidence Support": "Pending SME Review",
        "Non-Numeric Field": "N/A",
    }

    # Exact and candidate key resolution
    assert extract_metric_value(sample_metrics, ["Classifier Accuracy (Held-out Test Split)"]) == 0.9455
    assert extract_metric_value(sample_metrics, ["Classifier Accuracy", "Other Key"]) == 0.9455
    assert extract_metric_value(sample_metrics, ["Lexical Retrieval Hit@3"]) == 0.9238
    assert extract_metric_value(sample_metrics, ["Semantic Retrieval Hit@3"]) == 0.9762

    # Missing keys must return default (None)
    assert extract_metric_value(sample_metrics, ["Nonexistent Metric"]) is None
    assert extract_metric_value(sample_metrics, ["Nonexistent Metric"], default=0.0) == 0.0

    # Non-numeric or text indicators must return default (None)
    assert extract_metric_value(sample_metrics, ["Approach D Human-Reviewed Evidence Support"]) is None
    assert extract_metric_value(sample_metrics, ["Non-Numeric Field"]) is None


def test_format_kpi_value():
    """Verify that KPI values format properly as percentages/floats, and missing values return 'N/A'."""
    assert format_kpi_value(0.9455, "{:.2%}") == "94.55%"
    assert format_kpi_value(0.9238, "{:.2%}") == "92.38%"
    assert format_kpi_value(0.9762, "{:.2%}") == "97.62%"
    assert format_kpi_value(0.9281, "{:.3f}") == "0.928"
    assert format_kpi_value(1.0, "{:.1%}") == "100.0%"

    # Missing / None values must display 'N/A', not '0.0%'
    assert format_kpi_value(None) == "N/A"
    assert format_kpi_value(None, "{:.2%}") == "N/A"
    assert format_kpi_value(np.nan, "{:.2%}") == "N/A"
    assert format_kpi_value(None, na_string="Pending") == "Pending"


def test_kpi_metrics_extraction_from_saved_results():
    """Verify KPI extraction from actual results/metrics.csv yields expected verified benchmark values."""
    metrics_csv = RESULTS_DIR / "metrics.csv"
    assert metrics_csv.exists()
    metrics_df = pd.read_csv(metrics_csv)
    metrics_dict = dict(zip(metrics_df["Metric"], metrics_df["Value"]))

    clf_acc = extract_metric_value(metrics_dict, [
        "Classifier Accuracy (Held-out Test Split)",
        "Classifier Accuracy"
    ])
    clf_f1 = extract_metric_value(metrics_dict, [
        "Classifier Macro-F1 (Held-out Test Split)",
        "Classifier Macro-F1"
    ])
    lex_hit3 = extract_metric_value(metrics_dict, [
        "Lexical Retrieval Hit@3 (Labelled Cases)",
        "Lexical Retrieval Hit@3"
    ])
    sem_hit3 = extract_metric_value(metrics_dict, [
        "Semantic Retrieval Hit@3 (Labelled Cases)",
        "Semantic Retrieval Hit@3"
    ])
    unc_esc = extract_metric_value(metrics_dict, [
        "Ambiguous Cases Human Escalation Rate",
        "Uncertainty Human Review Escalation Rate"
    ])
    unc_guardrail = extract_metric_value(metrics_dict, [
        "Ambiguous Cases Non-Definitive / Low Confidence",
        "Uncertainty Low Confidence / Non-Definitive"
    ])

    # Reconciled targets: 94.55%, 92.38%, 97.62%, 100.0%
    assert clf_acc == 0.9455
    assert format_kpi_value(clf_acc, "{:.2%}") == "94.55%"

    assert clf_f1 == 0.9281
    assert format_kpi_value(clf_f1, "{:.3f}") == "0.928"

    assert lex_hit3 == 0.9238
    assert format_kpi_value(lex_hit3, "{:.2%}") == "92.38%"

    assert sem_hit3 == 0.9762
    assert format_kpi_value(sem_hit3, "{:.2%}") == "97.62%"

    assert unc_esc == 1.0
    assert format_kpi_value(unc_esc, "{:.1%}") == "100.0%"

    assert unc_guardrail == 1.0
    assert format_kpi_value(unc_guardrail, "{:.0%}") == "100%"


def test_reconciled_retrieval_metrics_consistency():
    """Verify consistent single source of truth across CSVs for lexical and semantic retrieval."""
    metrics_csv = RESULTS_DIR / "metrics.csv"
    comp_csv = RESULTS_DIR / "comparison_table.csv"

    metrics_df = pd.read_csv(metrics_csv)
    m_dict = dict(zip(metrics_df["Metric"], metrics_df["Value"]))

    assert "Lexical Retrieval Recall@3 (Labelled Cases)" in m_dict
    assert float(m_dict["Lexical Retrieval Recall@3 (Labelled Cases)"]) == 0.6881

    assert "Semantic Retrieval Recall@3 (Labelled Cases)" in m_dict
    assert float(m_dict["Semantic Retrieval Recall@3 (Labelled Cases)"]) == 0.7286

    comp_df = pd.read_csv(comp_csv)
    approach_b = comp_df[comp_df["Approach"].str.contains("Approach B")].iloc[0]
    approach_d = comp_df[comp_df["Approach"].str.contains("Approach D")].iloc[0]

    assert "0.6881" in str(approach_b["Macro-F1"])
    assert "0.7286" in str(approach_d["Macro-F1"])


def test_ui_review_banners_wcag_contrast():
    """Verify that app.py review banners enforce WCAG AA contrast compliant styling."""
    app_path = Path(__file__).resolve().parent.parent / "app.py"
    content = app_path.read_text(encoding="utf-8")

    # Mandatory review banner must specify dark red text (#7F1D1D) on pale red (#FEE2E2)
    assert "#7F1D1D" in content, "Mandatory human review banner must use explicit contrast-compliant text color #7F1D1D"
    assert "banner-mandatory-review" in content

    # Standard review banner must specify dark green text (#064E3B) on pale green (#ECFDF5)
    assert "#064E3B" in content, "Standard review banner must use explicit contrast-compliant text color #064E3B"
    assert "banner-standard-review" in content

