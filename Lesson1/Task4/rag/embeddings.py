import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rag.config import Settings


def generate_embeddings(texts: list[str], settings: "Settings") -> np.ndarray:
    if not texts:
        return np.array([])

    backend = settings.embed_backend.lower()

    if backend == "ollama":
        return _generate_ollama_embeddings(texts, settings)
    elif backend == "azure":
        return _generate_azure_embeddings(texts, settings)
    elif backend == "local":
        return _generate_local_embeddings(texts, settings)
    else:
        raise ValueError(f"Unknown embed_backend: '{backend}'")


def _generate_ollama_embeddings(texts: list[str], settings: "Settings") -> np.ndarray:
    import requests
    url = f"{settings.ollama_base_url}/api/embeddings"
    embeddings = []
    for text in texts:
        response = requests.post(url, json={"model": settings.ollama_embed_model, "prompt": text}, timeout=60)
        response.raise_for_status()
        embeddings.append(response.json()["embedding"])
    return np.array(embeddings, dtype=np.float32)


def _generate_azure_embeddings(texts: list[str], settings: "Settings") -> np.ndarray:
    from openai import AzureOpenAI
    client = AzureOpenAI(
        api_key=settings.azure_api_key,
        azure_endpoint=settings.azure_endpoint,
        api_version=settings.azure_api_version,
    )
    response = client.embeddings.create(input=texts, model=settings.azure_embed_deployment)
    embeddings = [item.embedding for item in response.data]
    return np.array(embeddings, dtype=np.float32)


def _generate_local_embeddings(texts: list[str], settings: "Settings") -> np.ndarray:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise ImportError("sentence-transformers not installed.")

    if not hasattr(_generate_local_embeddings, "_model") or _generate_local_embeddings._model_name != settings.local_embed_model:
        print(f"Loading local embedding model: {settings.local_embed_model}")
        _generate_local_embeddings._model = SentenceTransformer(settings.local_embed_model)
        _generate_local_embeddings._model_name = settings.local_embed_model

    embeddings = _generate_local_embeddings._model.encode(texts, show_progress_bar=False)
    return np.array(embeddings, dtype=np.float32)
