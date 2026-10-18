"""
Vector index builder using ChromaDB with local persistence and Ollama nomic-embed-text.
Extracts, chunks, embeds, and stores procedure documents with metadata.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

from config.settings import (
    KNOWLEDGE_BASE_DIR,
    VECTOR_STORE_DIR,
    CHROMA_COLLECTION_NAME,
    OLLAMA_EMBED_MODEL,
)
from src.lexical_retrieval import load_procedure_documents
from src.ollama_client import OllamaClient


def chunk_procedure_document(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Splits a procedure document into coherent passages with preserved metadata.
    Creates:
    1. Triggers and Evidence section (for symptom matching)
    2. Verification Steps and Escalation section (for action matching)
    3. Complete Overview passage
    """
    raw_text = doc["raw_text"]
    proc_id = doc["procedure_id"]
    title = doc["title"]
    category = doc["category"]
    source_type = doc["source_type"]

    chunks = []

    # 1. Full Procedure Document Chunk
    chunks.append({
        "chunk_id": f"{proc_id}_full",
        "procedure_id": proc_id,
        "title": title,
        "category": category,
        "source_type": source_type,
        "section_type": "full_procedure",
        "text": raw_text.strip(),
    })

    # 2. Extract Trigger & Evidence Section if present
    trigger_match = raw_text.find("## Trigger Indicators")
    steps_match = raw_text.find("## Generic Verification Steps")
    missing_match = raw_text.find("## Missing Information to Collect")

    if trigger_match != -1 and steps_match != -1:
        trigger_section = raw_text[trigger_match:steps_match].strip()
        chunks.append({
            "chunk_id": f"{proc_id}_triggers_evidence",
            "procedure_id": proc_id,
            "title": title,
            "category": category,
            "source_type": source_type,
            "section_type": "triggers_and_evidence",
            "text": f"Procedure {proc_id}: {title} ({category})\n{trigger_section}",
        })

    # 3. Extract Steps & Escalation Section
    if steps_match != -1:
        steps_section = raw_text[steps_match:].strip()
        chunks.append({
            "chunk_id": f"{proc_id}_steps_escalation",
            "procedure_id": proc_id,
            "title": title,
            "category": category,
            "source_type": source_type,
            "section_type": "steps_and_escalation",
            "text": f"Procedure {proc_id}: {title} ({category})\n{steps_section}",
        })

    return chunks


class ProcedureVectorIndex:
    """Manages persistent ChromaDB index for procedure passages."""

    def __init__(
        self,
        persist_dir: Path = VECTOR_STORE_DIR,
        collection_name: str = CHROMA_COLLECTION_NAME,
        ollama_client: Optional[OllamaClient] = None,
    ):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.ollama_client = ollama_client or OllamaClient()
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize persistent Chroma client
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "SettleSense Illustrative Procedure Embeddings"}
        )

    def is_indexed(self) -> bool:
        """Returns True if the collection already contains passages."""
        return self.collection.count() > 0

    def build_index(self, kb_dir: Path = KNOWLEDGE_BASE_DIR, force_rebuild: bool = False) -> int:
        """
        Extracts, chunks, embeds, and stores all procedure documents in ChromaDB.
        Returns total number of chunks indexed.
        """
        if self.is_indexed() and not force_rebuild:
            print(f"Collection '{self.collection_name}' already contains {self.collection.count()} passages. Use force_rebuild=True to overwrite.")
            return self.collection.count()

        if force_rebuild and self.is_indexed():
            self.chroma_client.delete_collection(self.collection_name)
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "SettleSense Illustrative Procedure Embeddings"}
            )

        documents = load_procedure_documents(kb_dir)
        all_chunks = []
        for doc in documents:
            chunks = chunk_procedure_document(doc)
            all_chunks.extend(chunks)

        if not all_chunks:
            return 0

        chunk_texts = [c["text"] for c in all_chunks]
        chunk_ids = [c["chunk_id"] for c in all_chunks]
        chunk_metadatas = [
            {
                "procedure_id": c["procedure_id"],
                "title": c["title"],
                "category": c["category"],
                "source_type": c["source_type"],
                "section_type": c["section_type"],
            }
            for c in all_chunks
        ]

        # Generate dense embeddings via local Ollama
        print(f"Generating dense embeddings for {len(chunk_texts)} passages using {self.ollama_client.embed_model}...")
        embeddings = self.ollama_client.get_embeddings(chunk_texts)

        # Upsert into ChromaDB
        self.collection.upsert(
            ids=chunk_ids,
            documents=chunk_texts,
            metadatas=chunk_metadatas,
            embeddings=embeddings,
        )

        total_indexed = self.collection.count()
        print(f"Successfully indexed {total_indexed} passages into ChromaDB at {self.persist_dir}.")
        return total_indexed

