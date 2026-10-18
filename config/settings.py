"""
Configuration and settings module for SettleSense.
Provides configurable paths, Ollama endpoint URLs, model identifiers,
and taxonomy constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Root directory of the SettleSense project
BASE_DIR = Path(__file__).resolve().parent.parent

# Core Directory Paths
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
MODELS_DIR = BASE_DIR / "models"
VECTOR_STORE_DIR = BASE_DIR / "vector_store" / "chroma"
RESULTS_DIR = BASE_DIR / "results"
FIGURES_DIR = RESULTS_DIR / "figures"
DOCS_DIR = BASE_DIR / "docs"

# Ensure runtime directories exist
for directory in [DATA_DIR, KNOWLEDGE_BASE_DIR, MODELS_DIR, VECTOR_STORE_DIR.parent, RESULTS_DIR, FIGURES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Matplotlib cache directory to avoid permission issues in restricted environments
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

# Deterministic Seed
RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))

# Local Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_GEN_MODEL = os.getenv("OLLAMA_GEN_MODEL", "qwen3:4b")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))

# Six Canonical Failure Categories
CANONICAL_CATEGORIES = [
    "SSI_MISMATCH",
    "TRADE_DETAIL_MISMATCH",
    "SECURITIES_SHORTFALL",
    "CASH_SHORTFALL",
    "COUNTERPARTY_UNCONFIRMED",
    "SETTLEMENT_TIMING",
]

# Uncertainty Label for Ambiguous Cases
AMBIGUOUS_LABEL = "UNDETERMINED"

# Complete label space for outputs
ALL_LABELS = CANONICAL_CATEGORIES + [AMBIGUOUS_LABEL]

# RAG & Retrieval Settings
TOP_K_RETRIEVAL = 3
CHROMA_COLLECTION_NAME = "settlesense_procedures"

