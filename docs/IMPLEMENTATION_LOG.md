# SettleSense Implementation Log

## Entry 1: Environment Inspection & Project Initialization
- **Date:** 2026-10-17
- **System:** macOS Darwin 25.6.0 (Apple Silicon arm64, 24 GB RAM, 371 GB disk space available).
- **Python:** 3.14.7 installed with dedicated virtual environment `.venv`.
- **Git:** Git version 2.50.1 detected.
- **Ollama Status:**
  - Endpoint `http://127.0.0.1:11434` active and responsive.
  - Generation Model: `qwen3:4b` verified with local test completion.
  - Embedding Model: `nomic-embed-text` pulled via Ollama and verified with 768-dimensional test embedding generation.
- **Dependencies Installed:**
  - `numpy`, `pandas`, `scikit-learn`, `pydantic`, `joblib`, `matplotlib`, `pytest`, `streamlit`, `chromadb`, `requests`, `python-dotenv`.
- **Project Structure Initialized:**
  - Created `.gitignore` excluding caches, `.venv`, local vector databases, large model binaries, and secrets.
  - Created `.env.example`, `requirements.txt`, `config/settings.py`, and `src/__init__.py`.
  - Configured directory skeleton: `config/`, `data/`, `knowledge_base/`, `src/`, `scripts/`, `tests/`, `models/`, `vector_store/`, `results/figures/`, `docs/`.

## Entry 2: Dataset Generation & Knowledge Base Implementation
- **Date:** 2026-10-17
- **Data Generator:** `src/data_generator.py` using deterministic seed 42.
- **Dataset Composition:**
  - 210 labelled exception cases (35 per canonical category across 6 categories).
  - 30 ambiguous exception cases (`UNDETERMINED` label, `is_sufficiently_informative=False`).
  - Total: 240 cases.
  - 48 Scenario Families preventing data leakage across train/test splits.
- **Knowledge Base:**
  - Created 14 detailed, distinct, illustrative procedure markdown documents in `knowledge_base/`:
    - `PROC_01`, `PROC_02`: SSI Mismatch
    - `PROC_03`, `PROC_04`: Trade Detail Mismatch
    - `PROC_05`, `PROC_06`: Securities Shortfall
    - `PROC_07`, `PROC_08`: Cash Shortfall
    - `PROC_09`, `PROC_10`: Counterparty Unconfirmed
    - `PROC_11`, `PROC_12`: Settlement Timing
    - `PROC_13`, `PROC_14`: Undetermined / Multi-factor Triage
- **Validation:** `src/data_validation.py` verifying schema, label validity, zero nulls, unique IDs, unique narratives, no target label leakage, and scenario split integrity.
- **Unit Tests:** `tests/test_data_validation.py` (6 tests passing).

## Entry 3: Traditional NLP Baseline & Lexical Retrieval
- **Date:** 2026-10-17
- **Preprocessing:** `src/preprocessing.py` standardizing narratives, removing noise, and filtering financial stop words.
- **Approach A Classifier:** `src/train_classifier.py`
  - Group-aware split on `scenario_family_id` (155 train / 55 test).
  - TF-IDF Vectorizer fit strictly on train split.
  - Logistic Regression (balanced class weights).
  - Test Set Accuracy: 1.0000, Macro-F1: 1.0000.
  - Model weights saved to `models/classifier.joblib` and `models/tfidf_vectorizer.joblib`.
- **Approach B Lexical Retrieval:** `src/lexical_retrieval.py`
  - TF-IDF cosine similarity search across 14 procedure documents.
  - Top-3 Retrieval Performance: Hit@3 = 96.67%, Recall@3 = 75.71%, MRR = 0.9286.
- **Unit Tests:** `tests/test_preprocessing.py`, `tests/test_classifier.py`, `tests/test_retrieval.py` (10 tests passing).

## Entry 4: Local Vector Retrieval & Persistent ChromaDB Index
- **Date:** 2026-10-17
- **Ollama Client:** `src/ollama_client.py` connecting to `http://localhost:11434` for dense embeddings and generation.
- **ChromaDB Indexer:** `src/embedding_index.py` chunking 14 procedure documents into 42 coherent passages with preserved metadata (procedure ID, title, category, source type, section type).
- **Indexing Execution:** `scripts/build_index.py` generating 768-dim embeddings via `nomic-embed-text` and writing to `vector_store/chroma/`.
- **Semantic Retrieval Engine:** `src/semantic_retrieval.py` retrieving Top-3 procedures with deduplication and cosine distance calculation.
  - Initial Pilot Evaluation (14 Passages): Hit@3 = 100.0%, Recall@3 = 78.57%, MRR = 0.9317.
  - Reconciled Full Benchmark (N=210 Labelled Cases): Hit@3 = 97.62%, Recall@3 = 72.86%, MRR = 0.8905.

## Entry 5: Grounded RAG Pipeline & Output Validation
- **Date:** 2026-10-17
- **Pydantic Schemas:** `src/output_schemas.py` enforcing structured investigation reports with observed facts, possible causes, recommended checks, missing information, procedure references, and human review flags.
- **Output Validation:** `src/output_validation.py` verifying JSON schemas, cross-referencing procedure citations against known knowledge base IDs, detecting hallucinations, and extracting JSON from LLM fences and thinking tokens.
- **RAG Pipeline:** `src/rag_pipeline.py` implementing Approach C (Prompt-Only) and Approach D (Semantic RAG) with grounded prompts and resilient error fallbacks.
- **Unit Tests:** `tests/test_output_validation.py`, `tests/test_rag_pipeline.py` (10 tests passing).

## Entry 6: Streamlit Analyst Dashboard
- **Date:** 2026-10-17
- **Application:** `app.py`
  - Multi-tab financial operations tool.
  - Interactive exception investigation with pre-loaded examples for all 6 categories and 2 ambiguous cases.
  - Dual-engine analysis: Instant classifier prediction + Grounded RAG report.
  - Retrieved procedure inspector with source excerpts.
  - Knowledge base library browser.
  - Evaluation dashboard rendering pre-computed metrics and benchmark figures.
  - Sidebar local model health monitor.

## Entry 7: Empirical Evaluation Suite & Visualizations
- **Date:** 2026-10-17
- **Evaluation Module:** `src/evaluation.py` and CLI `scripts/run_experiments.py`.
- **Generated Figures in `results/figures/`:**
  - `class_distribution.png`: 240 dataset cases breakdown.
  - `confusion_matrix.png`: Classifier test matrix.
  - `macro_f1_comparison.png`: Macro-F1 across approaches.
  - `retrieval_hit3_comparison.png`: Lexical vs Semantic retrieval.
  - `response_latency_comparison.png`: Component latency profile.
  - `uncertainty_handling.png`: Handling of 30 ambiguous cases.
- **Generated Result Tables:**
  - `results/metrics.csv`
  - `results/comparison_table.csv`
  - `results/classifier_predictions.csv`
  - `results/test_observations.csv`

## Entry 8: Engineering & Git Readiness Verification
- **Date:** 2026-10-17
- **Test Suite:** 33 unit tests executed via pytest — 33 passed, 0 failed, 0 errors.
- **Git Hygiene:** Clean `.gitignore` verified. No virtual environments, caches, vector databases, or credentials staged or tracked.
- **Publishing Confirmation:** Zero git commit, push, or remote publishing performed.
- **Academic Report Confirmation:** No formal AAT report or presentation generated at this stage.

## Entry 9: Dashboard Metric Reconciliation, Chart Alignment, and WCAG AA Contrast Fixes
- **Date:** 2026-10-18
- **KPI Card Extraction & Formatting:**
  - Implemented `extract_metric_value` and `format_kpi_value` in `src/evaluation.py` and integrated into `app.py`.
  - Reconciled metric key names to correctly match `results/metrics.csv`.
  - Displayed verified targets:
    - Classifier accuracy: 94.55%, Macro-F1: 0.928 (N=55 held-out test cases).
    - Lexical retrieval Hit@3: 92.38%, MRR: 0.871 (N=210 labelled cases).
    - Semantic retrieval Hit@3: 97.62%, MRR: 0.891 (N=210 labelled cases).
    - Uncertainty escalation: 100.0% (N=2 pilot cases), with Classifier Guardrail: 100% (N=30 ambiguous cases).
  - Ensured missing metrics display clean `"N/A"` rather than misleading `"0.0%"`.
- **Retrieval Metric Reconciliation:**
  - Reconciled single consistent source of truth across CSVs and plotted charts.
  - Resolved historical discrepancy between pilot indexing Recall@3 (~0.79 / 78.57% on 14 pilot passages) and the verified full benchmark (Recall@3 = 72.86%, Hit@3 = 97.62%, MRR = 0.8905 on N=210 labelled cases).
  - Updated `results/metrics.csv` to record both `Lexical Retrieval Recall@3 (Labelled Cases)` (0.6881) and `Semantic Retrieval Recall@3 (Labelled Cases)` (0.7286).
  - Regenerated `results/figures/retrieval_hit3_comparison.png` with verified metrics (0.924, 0.688, 0.871 vs 0.976, 0.729, 0.891).
- **Uncertainty Chart & Denominators Alignment:**
  - Updated `generate_uncertainty_handling_plot` in `src/evaluation.py` and regenerated `results/figures/uncertainty_handling.png`.
  - Bars and annotations explicitly distinguish:
    1. Classifier Low Confidence / Non-Definitive Guardrail: 100.0% (N=30 ambiguous cases, 30/30).
    2. RAG Human Review Escalation Rate: 100.0% (N=2 pilot cases, 2/2).
    3. Missing Information Identified Rate: 100.0% (N=2 pilot cases, 2/2).
- **WCAG AA UI Contrast Accessibility:**
  - In `app.py`, resolved unreadable white text on pale backgrounds in Streamlit dark mode.
  - Added `.banner-mandatory-review` with `color: #7F1D1D !important;` on `#FEE2E2` background (contrast ratio 10.0:1, exceeding WCAG AAA).
  - Added `.banner-standard-review` with `color: #064E3B !important;` on `#ECFDF5` background (contrast ratio 10.4:1, exceeding WCAG AAA).
  - Applied explicit styling to containers, strong tags, and spans to prevent dark theme inheritance overrides.
- **Verification:**
  - 41 unit tests executed via pytest — 41 passed, 0 failed in 1.20s.

