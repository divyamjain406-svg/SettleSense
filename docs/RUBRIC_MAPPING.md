# SettleSense Academic Demonstration & Rubric Mapping

This document outlines how the architectural components and engineering decisions of SettleSense map directly to the technical evaluation criteria for an offline AI/NLP capstone demonstration.

---

## 1. Rubric Mapping Matrix

| Technical Rubric Criterion | Implementation Component | Source Code & Artifact Reference | Demonstration Talking Points |
|---|---|---|---|
| **Problem Formulation & Financial Domain Knowledge** | Securities settlement exception investigation taxonomy (6 canonical classes + ambiguous class). | `config/settings.py`, `docs/DATASET_CARD.md`, `knowledge_base/` | Explain settlement failure lifecycle (DvP, Nostro cash deficits, inventory lockups, market cutoffs, SSI discrepancies). |
| **Deterministic Data Engineering** | Synthetic dataset generator with 240 cases, group-aware scenario family IDs, seed 42. | `src/data_generator.py`, `scripts/generate_dataset.py`, `data/` | Explain why `scenario_family_id` is essential to prevent data leakage during train/test splits. |
| **Traditional NLP Baseline** | Text normalization, TF-IDF vectorization, Logistic Regression classifier with GroupShuffleSplit. | `src/preprocessing.py`, `src/train_classifier.py`, `models/` | Demonstrate lightweight baseline classifier achieving rapid triage (~1.2 ms) with 100% Macro-F1 on test partition. |
| **Information Retrieval (IR) Baseline** | TF-IDF Cosine Similarity Lexical Retriever over 14 markdown procedure documents. | `src/lexical_retrieval.py` | Contrast keyword retrieval against dense semantic retrieval (Hit@3 = 96.7% vs 100%). |
| **Dense Embeddings & Vector Databases** | Local ChromaDB persistence with 768-dim `nomic-embed-text` embeddings generated via Ollama. | `src/embedding_index.py`, `src/semantic_retrieval.py`, `scripts/build_index.py` | Explain passage chunking, cosine distance metrics, and top-3 procedure deduplication. |
| **Retrieval-Augmented Generation (RAG)** | Grounded prompt construction, citation grounding, local `qwen3:4b` inference via Ollama. | `src/rag_pipeline.py` | Explain how grounding prompts with procedure excerpts eliminates hallucinations and anchors recommendations. |
| **Output Validation & Guardrails** | Pydantic schema validation, citation cross-checking, hallucination detection, JSON fence extraction. | `src/output_schemas.py`, `src/output_validation.py` | Explain why financial copilot outputs must distinguish observed evidence from hypothetical causes. |
| **Uncertainty & Human Escalation** | Separate evaluation on 30 `UNDETERMINED` cases; mandatory human review enforcement. | `src/output_schemas.py`, `results/figures/uncertainty_handling.png` | Demonstrate how copilot safely handles truncated or contradictory evidence rather than making false claims. |
| **Empirical Evaluation & Visualizations** | End-to-end benchmark suite measuring Accuracy, Macro-F1, Hit@3, MRR, Latency, and generating plots. | `src/evaluation.py`, `scripts/run_experiments.py`, `results/figures/` | Walk through confusion matrix, latency trade-offs (1.2 ms vs 33s), and empirical metric tables. |
| **Production Software Engineering** | 33 automated pytest unit tests, virtual environment, clean `.gitignore`, Streamlit dashboard. | `tests/`, `app.py`, `pytest.ini`, `requirements.txt` | Highlight modular design, complete unit test coverage (100% passing), and offline execution. |

---

## 2. Key Architectural Takeaways for Students & Reviewers

1. **Dual-Engine Synergies**: Fast traditional classifiers (Approach A) provide instant category hypothesis and operational triage, while Semantic RAG (Approach D) provides deep contextual explanations, verification checklists, and audit references.
2. **Offline Local Sovereignty**: All embeddings and generative inferences run on local silicon via Ollama, protecting sensitive trade data without cloud dependency.
3. **Safety by Design**: Mandatory human review escalation for uncertain cases ensures the copilot operates strictly as an analyst assistant, never an autonomous decision maker.

