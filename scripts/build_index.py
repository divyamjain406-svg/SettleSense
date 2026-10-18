#!/usr/bin/env python3
"""
CLI script to build or rebuild the persistent ChromaDB procedure index.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
from src.embedding_index import ProcedureVectorIndex

def main():
    parser = argparse.ArgumentParser(description="Build SettleSense ChromaDB Procedure Vector Index")
    parser.add_argument("--force", action="store_true", help="Force rebuild existing collection")
    args = parser.parse_args()

    print("Initializing Procedure Vector Indexer...")
    indexer = ProcedureVectorIndex()

    print(f"Target ChromaDB directory: {indexer.persist_dir}")
    print(f"Collection: {indexer.collection_name}")

    count = indexer.build_index(force_rebuild=args.force)
    print(f"\nVector Indexing complete. Total indexed chunks: {count}")

if __name__ == "__main__":
    main()

