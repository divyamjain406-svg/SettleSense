"""
Approach B: TF-IDF Lexical Procedure Retrieval.
Indexes procedure markdown documents using TF-IDF and retrieves the Top-3
relevant procedures based on cosine similarity.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import re
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config.settings import KNOWLEDGE_BASE_DIR, TOP_K_RETRIEVAL
from src.preprocessing import normalize_narrative

def load_procedure_documents(kb_dir: Path = KNOWLEDGE_BASE_DIR) -> List[Dict[str, Any]]:
    """
    Parses all procedure markdown documents from knowledge_base directory.
    Extracts metadata: procedure_id, title, category, source_type, content.
    """
    documents = []
    for file_path in sorted(kb_dir.glob("PROC_*.md")):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        proc_id_match = re.search(r"\*\*Procedure ID:\*\*\s*(PROC_\d+)", text)
        title_match = re.search(r"\*\*Title:\*\*\s*(.+)", text)
        cat_match = re.search(r"\*\*Relevant Category:\*\*\s*(\w+)", text)
        source_match = re.search(r"\*\*Source Type:\*\*\s*(.+)", text)

        proc_id = proc_id_match.group(1).strip() if proc_id_match else file_path.stem
        title = title_match.group(1).strip() if title_match else file_path.stem
        category = cat_match.group(1).strip() if cat_match else "UNKNOWN"
        source_type = source_match.group(1).strip() if source_match else "Synthetic"

        documents.append({
            "procedure_id": proc_id,
            "title": title,
            "category": category,
            "source_type": source_type,
            "file_name": file_path.name,
            "raw_text": text,
            "clean_text": normalize_narrative(text),
        })

    return documents


class LexicalRetriever:
    """TF-IDF Cosine Similarity Search Engine for Procedure Documents."""

    def __init__(self, kb_dir: Path = KNOWLEDGE_BASE_DIR):
        self.kb_dir = kb_dir
        self.documents: List[Dict[str, Any]] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix: Optional[np.ndarray] = None
        self._build_index()

    def _build_index(self):
        """Builds TF-IDF index across all loaded procedure documents."""
        self.documents = load_procedure_documents(self.kb_dir)
        if not self.documents:
            return

        corpus = [doc["clean_text"] for doc in self.documents]
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    @property
    def is_ready(self) -> bool:
        return self.vectorizer is not None and self.tfidf_matrix is not None and len(self.documents) > 0

    def retrieve(self, query_text: str, top_k: int = TOP_K_RETRIEVAL) -> List[Dict[str, Any]]:
        """
        Retrieves top_k procedure documents matching query_text.
        Returns list of dicts with procedure_id, title, category, score, and text excerpt.
        """
        if not self.is_ready:
            return []

        clean_query = normalize_narrative(query_text)
        if not clean_query:
            return []

        query_vec = self.vectorizer.transform([clean_query])
        scores = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            doc = self.documents[idx]
            results.append({
                "procedure_id": doc["procedure_id"],
                "title": doc["title"],
                "category": doc["category"],
                "score": float(scores[idx]),
                "file_name": doc["file_name"],
                "excerpt": doc["raw_text"][:350] + ("..." if len(doc["raw_text"]) > 350 else ""),
                "full_text": doc["raw_text"],
            })

        return results


def evaluate_lexical_retrieval(test_df_path: Optional[Path] = None, top_k: int = 3) -> Dict[str, Any]:
    """
    Evaluates Hit@K and Recall@K of lexical retrieval on labelled cases.
    """
    from config.settings import DATA_DIR
    if test_df_path is None:
        test_df_path = DATA_DIR / "labeled_cases.csv"

    df = pd.read_csv(test_df_path)
    retriever = LexicalRetriever()

    hits = 0
    total = 0
    recalls = []
    rr_list = []

    for _, row in df.iterrows():
        relevant_ids = set(str(row["relevant_procedure_ids"]).split("|"))
        results = retriever.retrieve(row["case_description"], top_k=top_k)
        retrieved_ids = [r["procedure_id"] for r in results]

        # Hit@K (at least 1 relevant procedure retrieved in top K)
        matched = relevant_ids.intersection(set(retrieved_ids))
        if len(matched) > 0:
            hits += 1

        # Recall@K
        recalls.append(len(matched) / len(relevant_ids) if relevant_ids else 0.0)

        # Reciprocal Rank (MRR)
        rank = 0
        for i, ret_id in enumerate(retrieved_ids):
            if ret_id in relevant_ids:
                rank = 1.0 / (i + 1)
                break
        rr_list.append(rank)
        total += 1

    hit_at_k = hits / total if total > 0 else 0.0
    mean_recall = float(np.mean(recalls)) if recalls else 0.0
    mrr = float(np.mean(rr_list)) if rr_list else 0.0

    return {
        "method": f"Lexical TF-IDF (Top-{top_k})",
        "total_cases_evaluated": total,
        f"hit@{top_k}": hit_at_k,
        f"recall@{top_k}": mean_recall,
        "mrr": mrr,
    }


if __name__ == "__main__":
    retriever = LexicalRetriever()
    print(f"Lexical Retriever indexed {len(retriever.documents)} procedures.")
    sample_query = "Our safekeeping account failed because counterparty instructed a different depository account"
    results = retriever.retrieve(sample_query, top_k=3)
    print(f"\nSample Query: '{sample_query}'")
    for r in results:
        print(f"  - [{r['score']:.3f}] {r['procedure_id']}: {r['title']} ({r['category']})")

    eval_res = evaluate_lexical_retrieval()
    print("\nLexical Retrieval Evaluation:")
    for k, v in eval_res.items():
        print(f"  - {k}: {v}")
