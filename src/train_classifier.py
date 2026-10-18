"""
Approach A: TF-IDF + Logistic Regression Multiclass Classifier.
Trains on labelled settlement cases using group-aware train/test splitting
to prevent scenario family leakage.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typing import Dict, Any, Tuple, Optional
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import GroupShuffleSplit

from config.settings import (
    DATA_DIR,
    MODELS_DIR,
    RESULTS_DIR,
    RANDOM_SEED,
    CANONICAL_CATEGORIES,
)
from src.preprocessing import normalize_narrative

MODEL_PATH = MODELS_DIR / "classifier.joblib"
VECTORIZER_PATH = MODELS_DIR / "tfidf_vectorizer.joblib"
METRICS_PATH = RESULTS_DIR / "classifier_metrics.json"

def prepare_data(data_path: Optional[Path] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Loads labelled cases and performs group-aware train/test split on scenario_family_id.
    Ensures no scenario family overlaps between splits.
    """
    if data_path is None:
        data_path = DATA_DIR / "labeled_cases.csv"

    df = pd.read_csv(data_path)
    
    # Filter only informative cases
    df = df[df["is_sufficiently_informative"] == True].copy()
    df["clean_description"] = df["case_description"].apply(normalize_narrative)

    # GroupShuffleSplit ensures all variants of a scenario family stay together
    gss = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=RANDOM_SEED)
    train_idx, test_idx = next(gss.split(df, groups=df["scenario_family_id"]))

    train_df = df.iloc[train_idx].copy()
    test_df = df.iloc[test_idx].copy()

    return train_df, test_df


def train_and_evaluate(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame
) -> Tuple[LogisticRegression, TfidfVectorizer, Dict[str, Any], pd.DataFrame]:
    """
    Fits TF-IDF vectorizer strictly on train_df, fits LogisticRegression,
    and calculates complete evaluation metrics on test_df.
    """
    # 1. Vectorization (Fit strictly on training set)
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True
    )
    X_train = vectorizer.fit_transform(train_df["clean_description"])
    y_train = train_df["expected_category"].values

    X_test = vectorizer.transform(test_df["clean_description"])
    y_test = test_df["expected_category"].values

    # 2. Train Logistic Regression
    clf = LogisticRegression(
        C=2.0,
        max_iter=1000,
        random_state=RANDOM_SEED,
        class_weight="balanced"
    )
    clf.fit(X_train, y_train)

    # 3. Predict on Test Set
    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)

    # 4. Evaluation Metrics
    accuracy = float(accuracy_score(y_test, y_pred))
    macro_precision = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
    macro_recall = float(recall_score(y_test, y_pred, average="macro", zero_division=0))
    macro_f1 = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

    cm = confusion_matrix(y_test, y_pred, labels=CANONICAL_CATEGORIES).tolist()
    report = classification_report(y_test, y_pred, labels=CANONICAL_CATEGORIES, output_dict=True, zero_division=0)

    metrics = {
        "model_type": "TF-IDF + Logistic Regression",
        "train_samples": int(len(train_df)),
        "test_samples": int(len(test_df)),
        "train_scenario_families": int(train_df["scenario_family_id"].nunique()),
        "test_scenario_families": int(test_df["scenario_family_id"].nunique()),
        "accuracy": accuracy,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "confusion_matrix": cm,
        "labels": CANONICAL_CATEGORIES,
        "classification_report": report,
    }

    # Record predictions table
    test_pred_df = test_df[["case_id", "scenario_family_id", "expected_category"]].copy()
    test_pred_df["predicted_category"] = y_pred
    max_probs = [float(np.max(p)) for p in y_prob]
    test_pred_df["prediction_confidence"] = max_probs
    test_pred_df["is_correct"] = (test_pred_df["expected_category"] == test_pred_df["predicted_category"])

    return clf, vectorizer, metrics, test_pred_df


def save_artifacts(
    clf: LogisticRegression,
    vectorizer: TfidfVectorizer,
    metrics: Dict[str, Any],
    predictions_df: pd.DataFrame
):
    """Saves model weights, vectorizer, metrics json, and predictions csv."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(clf, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    import json
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    predictions_path = RESULTS_DIR / "classifier_predictions.csv"
    predictions_df.to_csv(predictions_path, index=False)


class SettlementClassifier:
    """Inference wrapper for loading and scoring with the trained classifier."""

    def __init__(self, model_path: Path = MODEL_PATH, vectorizer_path: Path = VECTORIZER_PATH):
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        self.clf: Optional[LogisticRegression] = None
        self.vectorizer: Optional[TfidfVectorizer] = None
        self._load()

    def _load(self):
        if self.model_path.exists() and self.vectorizer_path.exists():
            self.clf = joblib.load(self.model_path)
            self.vectorizer = joblib.load(self.vectorizer_path)

    @property
    def is_ready(self) -> bool:
        return self.clf is not None and self.vectorizer is not None

    def predict(self, raw_text: str) -> Dict[str, Any]:
        """Predicts category and probability distribution for a single narrative."""
        if not self.is_ready:
            raise RuntimeError("Classifier models not found. Please train the classifier first.")

        clean = normalize_narrative(raw_text)
        if not clean:
            return {
                "predicted_category": "UNDETERMINED",
                "confidence": 0.0,
                "probabilities": {cat: 0.0 for cat in CANONICAL_CATEGORIES},
            }

        vec = self.vectorizer.transform([clean])
        pred_label = self.clf.predict(vec)[0]
        probs = self.clf.predict_proba(vec)[0]
        prob_dict = {cls: float(p) for cls, p in zip(self.clf.classes_, probs)}

        return {
            "predicted_category": pred_label,
            "confidence": float(np.max(probs)),
            "probabilities": prob_dict,
        }


def main():
    print("Preparing group-aware split on labelled settlement cases...")
    train_df, test_df = prepare_data()
    print(f"Train set: {len(train_df)} cases across {train_df['scenario_family_id'].nunique()} families")
    print(f"Test set:  {len(test_df)} cases across {test_df['scenario_family_id'].nunique()} families")

    print("\nTraining TF-IDF + Logistic Regression classifier...")
    clf, vectorizer, metrics, test_pred_df = train_and_evaluate(train_df, test_df)

    save_artifacts(clf, vectorizer, metrics, test_pred_df)

    print("\nTraining Complete! Baseline Evaluation Results:")
    print(f"  - Accuracy:         {metrics['accuracy']:.4f}")
    print(f"  - Macro Precision:  {metrics['macro_precision']:.4f}")
    print(f"  - Macro Recall:     {metrics['macro_recall']:.4f}")
    print(f"  - Macro F1-Score:   {metrics['macro_f1']:.4f}")
    print(f"  - Weighted F1-Score:{metrics['weighted_f1']:.4f}")

    print("\nPer-Class Metrics:")
    for cat in CANONICAL_CATEGORIES:
        cat_metrics = metrics["classification_report"].get(cat, {})
        p = cat_metrics.get("precision", 0.0)
        r = cat_metrics.get("recall", 0.0)
        f1 = cat_metrics.get("f1-score", 0.0)
        support = cat_metrics.get("support", 0)
        print(f"  - {cat:<26}: P={p:.2f}, R={r:.2f}, F1={f1:.2f} (support={support})")

if __name__ == "__main__":
    main()
