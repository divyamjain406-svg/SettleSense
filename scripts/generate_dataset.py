#!/usr/bin/env python3
"""
CLI script to generate and validate the SettleSense synthetic dataset.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from src.data_generator import save_dataset
from src.data_validation import run_all_dataset_validations

def main():
    print("Generating SettleSense synthetic settlement cases dataset (Seed 42)...")
    paths = save_dataset()

    print("\nDataset files generated successfully:")
    for key, path in paths.items():
        print(f"  - {key}: {path}")

    # Run validation battery on full dataset
    df = pd.read_csv(paths["settlement_cases"])
    validation_results = run_all_dataset_validations(df)

    print("\nValidation Summary:")
    for check, res in validation_results.items():
        if check in ["overall_passed", "all_errors"]:
            continue
        status = "PASSED" if res["passed"] else "FAILED"
        print(f"  - {check:<22}: {status}")

    if not validation_results["overall_passed"]:
        print("\nValidation Errors Encountered:")
        for err in validation_results["all_errors"]:
            print(f"  [ERROR] {err}")
        sys.exit(1)
    else:
        print("\nAll dataset validations passed successfully!")
        print(f"Total Cases: {len(df)}")
        print(f"Category Counts:\n{df['expected_category'].value_counts().to_string()}")

if __name__ == "__main__":
    main()

