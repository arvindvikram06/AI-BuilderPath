import io
from pathlib import Path
from typing import Union


def load_documents(data_dir: Path) -> list[dict]:
    documents = []
    supported = {".md", ".txt", ".pdf"}

    for filepath in sorted(data_dir.iterdir()):
        if filepath.suffix.lower() not in supported:
            continue
        try:
            text = _read_file(filepath)
            if text.strip():
                documents.append({"source": filepath.name, "text": text})
                print(f"Loaded: {filepath.name} ({len(text):,} chars)")
        except Exception as e:
            print(f"Failed to load {filepath.name}: {e}")

    return documents


def load_from_bytes(file_bytes: bytes, filename: str) -> dict:
    suffix = Path(filename).suffix.lower()

    if suffix in (".md", ".txt"):
        text = file_bytes.decode("utf-8", errors="ignore")
    elif suffix == ".pdf":
        text = _extract_pdf_from_bytes(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Supported: .md, .txt, .pdf")

    return {"source": filename, "text": text}


def _read_file(filepath: Path) -> str:
    suffix = filepath.suffix.lower()
    if suffix in (".md", ".txt"):
        return filepath.read_text(encoding="utf-8", errors="ignore")
    elif suffix == ".pdf":
        return _extract_pdf_text(filepath)
    return ""


def _extract_pdf_text(filepath: Path) -> str:
    try:
        import fitz
        doc = fitz.open(str(filepath))
        pages = [page.get_text() for page in doc]
        doc.close()
        return "\n\n".join(pages)
    except ImportError:
        raise ImportError("PyMuPDF not installed.")


def _extract_pdf_from_bytes(file_bytes: bytes) -> str:
    try:
        import fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages = [page.get_text() for page in doc]
        doc.close()
        return "\n\n".join(pages)
    except ImportError:
        raise ImportError("PyMuPDF not installed.")
