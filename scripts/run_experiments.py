#!/usr/bin/env python3
"""
CLI script to run all SettleSense experimental evaluations, generate metrics,
tables, and comparison figures.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
from src.evaluation import run_full_experimental_evaluation

def main():
    parser = argparse.ArgumentParser(description="Run SettleSense Experimental Evaluations")
    parser.add_argument("--llm_samples", type=int, default=6, help="Number of test cases for LLM comparison")
    args = parser.parse_args()

    print("=================================================================")
    print(" SettleSense: Starting Full Experimental Evaluation Protocol")
    print("=================================================================\n")

    results = run_full_experimental_evaluation(eval_llm_sample_size=args.llm_samples)

    print("\n=================================================================")
    print(" SettleSense: Evaluation Completed Successfully")
    print("=================================================================")

if __name__ == "__main__":
    main()

