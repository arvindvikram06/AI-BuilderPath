import json
import numpy as np
from pathlib import Path


class VectorStore:
    EMBEDDINGS_FILE = "embeddings.npy"
    CHUNKS_FILE = "chunks.json"

    def __init__(self):
        self._embeddings: np.ndarray | None = None
        self._chunks: list[dict] = []

    def add_documents(self, chunks: list[dict], embeddings: np.ndarray) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError(f"Mismatch: {len(chunks)} chunks vs {len(embeddings)} embeddings")

        normalised = _normalize_l2(embeddings)

        if self._embeddings is None:
            self._embeddings = normalised
        else:
            self._embeddings = np.vstack([self._embeddings, normalised])

        self._chunks.extend(chunks)

    def similarity_search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[dict]:
        if self.is_empty():
            return []

        query_norm = _normalize_l2(query_embedding.reshape(1, -1))[0]
        scores = self._embeddings @ query_norm
        
        top_k = min(top_k, len(scores))
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append({
                "source": self._chunks[idx]["source"],
                "text": self._chunks[idx]["text"],
                "score": float(scores[idx]),
            })

        return results

    def is_empty(self) -> bool:
        return self._embeddings is None or len(self._embeddings) == 0

    def count(self) -> int:
        return len(self._chunks)

    def persist(self, index_dir: Path) -> None:
        index_dir.mkdir(parents=True, exist_ok=True)
        if self._embeddings is not None:
            np.save(index_dir / self.EMBEDDINGS_FILE, self._embeddings)
        with open(index_dir / self.CHUNKS_FILE, "w", encoding="utf-8") as f:
            json.dump(self._chunks, f, ensure_ascii=False, indent=2)
        print(f"Saved {self.count()} chunks to {index_dir}")

    def load_from_disk(self, index_dir: Path) -> bool:
        emb_path = index_dir / self.EMBEDDINGS_FILE
        chunks_path = index_dir / self.CHUNKS_FILE

        if not emb_path.exists() or not chunks_path.exists():
            return False

        self._embeddings = np.load(str(emb_path))
        with open(chunks_path, "r", encoding="utf-8") as f:
            self._chunks = json.load(f)

        print(f"Loaded {self.count()} chunks from {index_dir}")
        return True


def _normalize_l2(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1e-10, norms)
    return matrix / norms
