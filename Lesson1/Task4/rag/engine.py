from typing import Generator, TYPE_CHECKING

if TYPE_CHECKING:
    from rag.config import Settings

from rag.document_loader import load_documents, load_from_bytes
from rag.text_splitter import split_documents
from rag.embeddings import generate_embeddings
from rag.vector_store import VectorStore
from rag.retriever import retrieve, build_context
from rag.llm_client import stream_completion

SYSTEM_PROMPT = """You are RAG Bot, a helpful and professional assistant.
If the user is just saying hello or making small talk, respond politely and naturally.

For factual questions, answer accurately using ONLY the context provided below.
If the answer is not found in the context, respond exactly with: "I don't have that information."
Do NOT make up information or use outside knowledge.

Context:
{context}"""


def build_index(settings: "Settings") -> VectorStore:
    print("Building knowledge base index...")
    documents = load_documents(settings.data_dir)
    if not documents:
        raise FileNotFoundError(f"No documents found in {settings.data_dir}")
    
    chunks = split_documents(documents, settings.chunk_size, settings.chunk_overlap)
    texts = [c["text"] for c in chunks]
    embeddings = generate_embeddings(texts, settings)
    
    store = VectorStore()
    store.add_documents(chunks, embeddings)
    store.persist(settings.index_dir)
    print(f"Index built: {store.count()} chunks saved.")
    return store


def load_or_build_index(settings: "Settings") -> VectorStore:
    store = VectorStore()
    if store.load_from_disk(settings.index_dir):
        return store
    return build_index(settings)


class RAGEngine:
    def __init__(self, settings: "Settings"):
        self.settings = settings
        self.base_store = load_or_build_index(settings)
        self.session_store = VectorStore()
        self._session_doc_count = 0

    def ingest_document(self, file_bytes: bytes, filename: str) -> int:
        doc = load_from_bytes(file_bytes, filename)
        chunks = split_documents([doc], self.settings.chunk_size, self.settings.chunk_overlap)
        texts = [c["text"] for c in chunks]
        embeddings = generate_embeddings(texts, self.settings)
        
        self.session_store.add_documents(chunks, embeddings)
        self._session_doc_count += 1
        return len(chunks)

    def query(
        self,
        query: str,
        history: list[dict],
        top_k_base: int | None = None,
        top_k_session: int | None = None,
    ) -> tuple[Generator[str, None, None], list[dict]]:
        top_k_base = top_k_base or self.settings.top_k_base
        top_k_session = top_k_session or self.settings.top_k_session

        base_results = retrieve(query, self.base_store, self.settings, top_k=top_k_base)
        session_results = retrieve(query, self.session_store, self.settings, top_k=top_k_session)

        for r in base_results:
            r["store_type"] = "base"
        for r in session_results:
            r["store_type"] = "session"

        all_results = base_results + session_results
        context = build_context(all_results)
        
        messages = [{"role": "system", "content": SYSTEM_PROMPT.format(context=context)}]
        for turn in history:
            messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": query})

        token_stream = stream_completion(messages, self.settings)
        return token_stream, all_results
