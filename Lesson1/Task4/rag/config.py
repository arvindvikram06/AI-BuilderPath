import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent

@dataclass
class Settings:
    llm_backend: str = field(default_factory=lambda: os.getenv("LLM_BACKEND", "groq"))
    embed_backend: str = field(default_factory=lambda: os.getenv("EMBED_BACKEND", "ollama"))

    groq_api_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    groq_model: str = field(default_factory=lambda: os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))

    azure_api_key: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY", ""))
    azure_endpoint: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_ENDPOINT", ""))
    azure_deployment: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"))
    azure_embed_deployment: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small"))
    azure_api_version: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"))

    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    claude_model: str = field(default_factory=lambda: os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5"))

    ollama_base_url: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    ollama_model: str = field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama3.2"))
    ollama_embed_model: str = field(default_factory=lambda: os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"))

    local_embed_model: str = field(default_factory=lambda: os.getenv("LOCAL_EMBED_MODEL", "all-MiniLM-L6-v2"))

    chunk_size: int = field(default_factory=lambda: int(os.getenv("CHUNK_SIZE", "800")))
    chunk_overlap: int = field(default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "100")))
    top_k_base: int = field(default_factory=lambda: int(os.getenv("TOP_K_BASE", "3")))
    top_k_session: int = field(default_factory=lambda: int(os.getenv("TOP_K_SESSION", "2")))

    data_dir: Path = field(default_factory=lambda: BASE_DIR / "data")
    index_dir: Path = field(default_factory=lambda: BASE_DIR / "index")

    def __post_init__(self):
        self.index_dir.mkdir(parents=True, exist_ok=True)

def get_settings() -> Settings:
    return Settings()
