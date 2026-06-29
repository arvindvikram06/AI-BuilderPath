import re


def split_documents(documents: list[dict], chunk_size: int = 800, chunk_overlap: int = 100) -> list[dict]:
    all_chunks = []
    for doc in documents:
        chunks = split_text(doc["text"], chunk_size, chunk_overlap)
        for chunk in chunks:
            all_chunks.append({"source": doc["source"], "text": chunk})
    return all_chunks


def split_text(text: str, chunk_size: int = 800, chunk_overlap: int = 100) -> list[str]:
    text = _normalize_whitespace(text)
    if not text:
        return []
    sentences = _split_into_sentences(text)
    return _merge_into_chunks(sentences, chunk_size, chunk_overlap)


def _normalize_whitespace(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def _split_into_sentences(text: str) -> list[str]:
    paragraphs = text.split("\n\n")
    sentences = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        parts = re.split(r"(?<=[.!?])\s+", para)
        sentences.extend(s.strip() for s in parts if s.strip())
    return sentences


def _merge_into_chunks(sentences: list[str], chunk_size: int, chunk_overlap: int) -> list[str]:
    chunks = []
    current_parts: list[str] = []
    current_len = 0

    for sentence in sentences:
        sentence_len = len(sentence)
        if sentence_len > chunk_size:
            if current_parts:
                chunks.append(" ".join(current_parts))
                current_parts = []
                current_len = 0
            for hard_chunk in _split_by_character_limit(sentence, chunk_size, chunk_overlap):
                chunks.append(hard_chunk)
            continue

        if current_len + sentence_len + 1 > chunk_size and current_parts:
            chunk_text = " ".join(current_parts)
            chunks.append(chunk_text)
            overlap_text = chunk_text[-chunk_overlap:] if chunk_overlap > 0 else ""
            current_parts = [overlap_text] if overlap_text else []
            current_len = len(overlap_text)

        current_parts.append(sentence)
        current_len += sentence_len + 1

    if current_parts:
        chunks.append(" ".join(current_parts))

    return [c.strip() for c in chunks if c.strip()]


def _split_by_character_limit(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    return chunks
