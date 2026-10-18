#!/usr/bin/env python3
"""
CLI script to regenerate all evaluation results, benchmarks, and figures.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.evaluation import run_full_experimental_evaluation

def main():
    print("Regenerating all SettleSense evaluation results and figures...")
    run_full_experimental_evaluation(eval_llm_sample_size=6)
    print("Regeneration complete.")

if __name__ == "__main__":
    main()

