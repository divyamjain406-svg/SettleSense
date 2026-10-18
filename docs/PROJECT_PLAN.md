# SettleSense Project Plan

## 1. Project Identity & Objective
- **Project Name:** SettleSense
- **Full Title:** SettleSense: An Offline LLM-Based Securities Settlement Exception Investigation Copilot Using NLP, Semantic Retrieval, and Retrieval-Augmented Generation
- **Target Role:** Educational Prototype & Academic Demonstration
- **Key Architecture:** Local LLM (`qwen3:4b`), Local Embeddings (`nomic-embed-text`), Local Vector DB (ChromaDB), Traditional Classifier (TF-IDF + Logistic Regression), Streamlit UI.

## 2. Milestone Roadmap

### Milestone 1: Environment and Project Setup
- [x] Inspect local execution environment, hardware, RAM, and disk space.
- [x] Verify local Ollama daemon and model tags (`qwen3:4b`, `nomic-embed-text`).
- [x] Configure Python virtual environment and core dependencies.
- [x] Create project layout, `.gitignore`, `.env.example`, `requirements.txt`, and `config/settings.py`.
- [x] Write `docs/PROJECT_PLAN.md`, `docs/ARCHITECTURE.md`, and initial `README.md`.
- [x] Initialize `docs/IMPLEMENTATION_LOG.md`.

### Milestone 2: Dataset and Knowledge Base
- [x] Implement deterministic synthetic dataset generator (`src/data_generator.py`) with seed 42.
- [x] Generate 210 labelled exception cases (35 per 6 categories) and 30 ambiguous (`UNDETERMINED`) cases.
- [x] Implement data validation module (`src/data_validation.py`) checking schema, labels, leakage, and scenario families.
- [x] Create 14 concise, distinct, illustrative procedure markdown documents in `knowledge_base/` (`PROC_01.md` to `PROC_14.md`).
- [x] Create executable generation script `scripts/generate_dataset.py`.
- [x] Write unit tests for dataset determinism, schema, and split integrity (`tests/test_data_validation.py`).

### Milestone 3: Traditional NLP Baseline
- [x] Implement text preprocessing (`src/preprocessing.py`).
- [x] Implement train/test split avoiding scenario-family leakage.
- [x] Train TF-IDF + Logistic Regression classifier (`src/train_classifier.py`).
- [x] Compute classification baseline metrics: Accuracy, Precision, Recall, Macro-F1, Confusion Matrix.
- [x] Implement TF-IDF lexical procedure retrieval (`src/lexical_retrieval.py`).
- [x] Add unit tests for preprocessing, classifier, and lexical retrieval (`tests/test_preprocessing.py`, `tests/test_classifier.py`, `tests/test_retrieval.py`).

### Milestone 4: Local Vector Retrieval
- [x] Implement Ollama embedding integration client (`src/ollama_client.py`).
- [x] Implement persistent local ChromaDB indexer (`src/embedding_index.py`).
- [x] Implement semantic query engine with Top-3 retrieval (`src/semantic_retrieval.py`).
- [x] Preserve metadata (category, procedure ID, title, source type).
- [x] Create build index script (`scripts/build_index.py`).
- [x] Test semantic retrieval with mocked embeddings and real local embeddings.

### Milestone 5: RAG and Output Validation
- [x] Define Pydantic output schemas (`src/output_schemas.py`).
- [x] Implement citation and evidence validation (`src/output_validation.py`).
- [x] Implement prompt-only LLM inference (`Approach C`) without retrieval.
- [x] Implement complete Semantic RAG pipeline (`Approach D`) (`src/rag_pipeline.py`).
- [x] Handle uncertainty, missing fields, and malformed JSON gracefully.
- [x] Unit test schemas, validators, error handlers, and pipeline paths (`tests/test_output_validation.py`, `tests/test_rag_pipeline.py`).

### Milestone 6: Streamlit Application
- [x] Implement financial operations analyst dashboard (`app.py`).
- [x] Input area for case narrative and optional transaction attributes.
- [x] Pre-loaded example cases covering all categories and ambiguous cases.
- [x] Dual-engine analysis: Predicted candidate category + RAG investigation report.
- [x] Retrieved procedure inspection pane with source excerpts.
- [x] Evaluation view presenting baseline metrics, confusion matrix, and approach comparisons.
- [x] System health monitor for Ollama connectivity and model tag readiness.

### Milestone 7: Experimental Evaluation & Visualizations
- [x] Implement evaluation harness (`src/evaluation.py` and `scripts/run_experiments.py`).
- [x] Run Approach A (Classifier), Approach B (Lexical Retrieval), Approach C (Prompt-only LLM), Approach D (Semantic RAG).
- [x] Evaluate 30 `UNDETERMINED` cases separately for uncertainty handling.
- [x] Generate result tables (`metrics.csv`, `predictions.csv`, `comparison_table.csv`).
- [x] Generate visualization charts in `results/figures/`.

### Milestone 8: Final Engineering Verification
- [x] Run full test suite with pytest (33/33 tests passing).
- [x] Validate GitHub readiness and verify `.gitignore` integrity.
- [x] Document reproducibility and run commands in `README.md`.
- [x] Confirm no cloud inference, no remote APIs, and no unapproved git operations.
