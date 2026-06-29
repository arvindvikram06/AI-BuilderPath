import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rag.config import Settings
    from rag.vector_store import VectorStore

from rag.embeddings import generate_embeddings


def retrieve(query: str, store: "VectorStore", settings: "Settings", top_k: int = 5, score_threshold: float = 0.3) -> list[dict]:
    if store.is_empty():
        return []
    query_embedding = generate_embeddings([query], settings)[0]
    results = store.similarity_search(query_embedding, top_k=top_k)
    
    # Only keep results that are similar enough to the query
    filtered_results = [r for r in results if r["score"] >= score_threshold]
    return filtered_results


def build_context(results: list[dict]) -> str:
    if not results:
        return "No relevant documents were found in the knowledge base."

    parts = []
    for i, result in enumerate(results, start=1):
        source = result.get("source", "unknown")
        text = result.get("text", "").strip()
        parts.append(f"[{i}] Source: {source}\n{text}")

    return "\n\n".join(parts)
