"""
Semantic Retrieval Engine using local ChromaDB and Ollama nomic-embed-text.
Performs Top-K dense vector retrieval over indexed procedure passages.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
from typing import List, Dict, Any, Optional, Set
import numpy as np
import pandas as pd

from config.settings import (
    TOP_K_RETRIEVAL,
    DATA_DIR,
    CHROMA_COLLECTION_NAME,
    VECTOR_STORE_DIR,
)
from src.embedding_index import ProcedureVectorIndex
from src.ollama_client import OllamaClient
from src.preprocessing import clean_text


class SemanticRetriever:
    """Retrieves semantically related procedure passages using dense embeddings."""

    def __init__(
        self,
        vector_index: Optional[ProcedureVectorIndex] = None,
        ollama_client: Optional[OllamaClient] = None,
    ):
        self.ollama_client = ollama_client or OllamaClient()
        self.vector_index = vector_index or ProcedureVectorIndex(ollama_client=self.ollama_client)

    @property
    def is_ready(self) -> bool:
        return self.vector_index.is_indexed()

    def retrieve(
        self,
        query_text: str,
        top_k: int = TOP_K_RETRIEVAL,
        deduplicate_by_procedure: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top_k procedure passages matching query_text.
        Returns list of structured procedure evidence passages with metadata.
        """
        clean_query = clean_text(query_text)
        if not clean_query or not self.is_ready:
            return []

        # Generate query vector
        try:
            query_embeddings = self.ollama_client.get_embeddings(clean_query)
        except Exception:
            return []

        if not query_embeddings or not query_embeddings[0]:
            return []

        query_vec = query_embeddings[0]

        # Request more chunks if deduplicating by procedure ID
        n_request = top_k * 3 if deduplicate_by_procedure else top_k

        results = self.vector_index.collection.query(
            query_embeddings=[query_vec],
            n_results=min(n_request, self.vector_index.collection.count()),
            include=["documents", "metadatas", "distances"]
        )

        retrieved: List[Dict[str, Any]] = []
        seen_proc_ids: Set[str] = set()

        docs = results["documents"][0] if results["documents"] else []
        metas = results["metadatas"][0] if results["metadatas"] else []
        distances = results["distances"][0] if results["distances"] else []

        for doc_text, meta, dist in zip(docs, metas, distances):
            proc_id = meta.get("procedure_id", "UNKNOWN")

            if deduplicate_by_procedure and proc_id in seen_proc_ids:
                continue

            seen_proc_ids.add(proc_id)

            # Chroma default L2 distance or cosine distance to normalized similarity score
            # Approximate cosine similarity from cosine distance: sim = 1.0 - (dist / 2.0)
            similarity = max(0.0, 1.0 - (float(dist) / 2.0))

            retrieved.append({
                "procedure_id": proc_id,
                "title": meta.get("title", ""),
                "category": meta.get("category", ""),
                "source_type": meta.get("source_type", "Synthetic"),
                "section_type": meta.get("section_type", ""),
                "similarity_score": round(similarity, 4),
                "distance": round(float(dist), 4),
                "passage_text": doc_text,
                "excerpt": doc_text[:350] + ("..." if len(doc_text) > 350 else ""),
            })

            if len(retrieved) >= top_k:
                break

        return retrieved


def evaluate_semantic_retrieval(
    test_df_path: Optional[Path] = None,
    top_k: int = 3
) -> Dict[str, Any]:
    """
    Evaluates Hit@K, Recall@K, MRR, and retrieval latency of Semantic Retrieval.
    """
    if test_df_path is None:
        test_df_path = DATA_DIR / "labeled_cases.csv"

    df = pd.read_csv(test_df_path)
    retriever = SemanticRetriever()

    if not retriever.is_ready:
        return {
            "method": f"Semantic Dense Vector (Top-{top_k})",
            "error": "Vector store not indexed. Run build_index.py first."
        }

    hits = 0
    total = 0
    recalls = []
    rr_list = []
    latencies = []

    for _, row in df.iterrows():
        relevant_ids = set(str(row["relevant_procedure_ids"]).split("|"))
        t0 = time.time()
        results = retriever.retrieve(row["case_description"], top_k=top_k)
        latencies.append(time.time() - t0)

        retrieved_ids = [r["procedure_id"] for r in results]
        matched = relevant_ids.intersection(set(retrieved_ids))

        if len(matched) > 0:
            hits += 1

        recalls.append(len(matched) / len(relevant_ids) if relevant_ids else 0.0)

        rank = 0.0
        for i, ret_id in enumerate(retrieved_ids):
            if ret_id in relevant_ids:
                rank = 1.0 / (i + 1)
                break
        rr_list.append(rank)
        total += 1

    hit_at_k = hits / total if total > 0 else 0.0
    mean_recall = float(np.mean(recalls)) if recalls else 0.0
    mrr = float(np.mean(rr_list)) if rr_list else 0.0
    avg_latency = float(np.mean(latencies)) if latencies else 0.0

    return {
        "method": f"Semantic nomic-embed-text (Top-{top_k})",
        "total_cases_evaluated": total,
        f"hit@{top_k}": hit_at_k,
        f"recall@{top_k}": mean_recall,
        "mrr": mrr,
        "avg_latency_ms": round(avg_latency * 1000, 2),
    }


if __name__ == "__main__":
    retriever = SemanticRetriever()
    if not retriever.is_ready:
        print("Vector store not indexed yet. Building index now...")
        retriever.vector_index.build_index()

    sample_query = "Our safekeeping account failed because counterparty instructed a different depository account"
    results = retriever.retrieve(sample_query, top_k=3)
    print(f"\nSample Query: '{sample_query}'")
    for r in results:
        print(f"  - [{r['similarity_score']:.3f}] {r['procedure_id']}: {r['title']} ({r['category']})")

