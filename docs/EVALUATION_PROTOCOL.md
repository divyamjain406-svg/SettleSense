# SettleSense Evaluation Protocol

## 1. Protocol Purpose
This document establishes the scientific evaluation methodology, metrics, and experimental protocols used to benchmark SettleSense.
All reported scores are strictly computed by deterministic code executions against real test splits and local model inferences.

## 2. Experimental Approaches Evaluated

| ID | Approach Name | Model / Vector Store | Scope & Objective |
|---|---|---|---|
| **Approach A** | TF-IDF + Logistic Regression | scikit-learn Logistic Regression | Supervised baseline for fast category triage. Evaluated on unseen scenario families. |
| **Approach B** | Lexical Retrieval Baseline | TF-IDF Vectors + Cosine Similarity | Keyword search over procedure passages to evaluate lexical matching quality. |
| **Approach C** | Prompt-Only Local LLM | `qwen3:4b` (via Ollama) | Zero-shot generation using only case facts (no retrieved procedure context). |
| **Approach D** | Semantic Retrieval + Grounded RAG | `nomic-embed-text` + ChromaDB + `qwen3:4b` | Dense semantic retrieval + grounded RAG prompt with citation and schema validation. |

## 3. Metric Formulations

### 3.1 Classification Metrics (Approach A & C/D Categorization)
- **Accuracy:** Proportion of correctly predicted failure categories on the test set.
  $$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$
- **Macro Precision, Recall, and F1-Score:** Unweighted arithmetic mean across all canonical categories, penalizing class imbalance.
  $$\text{Macro-F1} = \frac{1}{|C|} \sum_{c \in C} F1_c$$
- **Confusion Matrix:** $6 \times 6$ contingency table tracking misclassifications across canonical categories.

### 3.2 Retrieval Metrics (Approach B & D)
- **Hit@K (K=3):** Binary indicator whether at least one ground-truth procedure appears in the Top-K retrieved passages.
  $$\text{Hit@K} = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(\text{Relevant}_i \cap \text{Retrieved}_{i, K} \neq \emptyset)$$
- **Recall@K (K=3):** Fraction of relevant procedure IDs retrieved in the Top-K results.
  $$\text{Recall@K} = \frac{1}{N} \sum_{i=1}^N \frac{|\text{Relevant}_i \cap \text{Retrieved}_{i, K}|}{|\text{Relevant}_i|}$$
- **Mean Reciprocal Rank (MRR):** Measures rank position of the first relevant procedure document.
  $$\text{MRR} = \frac{1}{N} \sum_{i=1}^N \frac{1}{\text{rank}_i}$$

### 3.3 Generation & RAG Safety Metrics
- **Citation Validity Rate:** Ratio of valid cited procedure IDs that exist in the local knowledge base to total cited IDs.
  $$\text{Citation Validity} = \frac{|\text{Cited} \cap \text{Known KB IDs}|}{|\text{Cited}|}$$
- **Pydantic Schema Conformance:** Binary validation verifying that the LLM response parses into `SettlementInvestigationReport` without missing fields.
- **Uncertainty Escalation Rate:** Proportion of the 30 ambiguous/UNDETERMINED cases correctly flagged for mandatory human review (`requires_human_review = True`).
- **Mean & Median Latency:** End-to-end processing duration per request in milliseconds.

## 4. Leakage Prevention Protocol
1. **Scenario-Family Grouping:** Paraphrased or variant cases derived from the same underlying situation share a common `scenario_family_id`.
2. **Disjoint Partitioning:** Train and test splits are partitioned using `GroupShuffleSplit`. No `scenario_family_id` exists in both sets.
3. **No Target Leakage in Features:** Target category names (`expected_category`) and evaluation evidence are stripped from inputs during classification, retrieval queries, and LLM prompts.

