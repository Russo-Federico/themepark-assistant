from pathlib import Path

import pypdf

from config import CHUNK_OVERLAP_TOKENS, CHUNK_SIZE_TOKENS


def extract_text(file_path: Path) -> str:
    if file_path.suffix.lower() == ".pdf":
        reader = pypdf.PdfReader(str(file_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return file_path.read_text(encoding="utf-8")


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE_TOKENS,
    overlap: int = CHUNK_OVERLAP_TOKENS,
) -> list[str]:
    """Splits text into overlapping chunks. Tokens are approximated as
    whitespace-separated words (no tokenizer dependency in this phase)."""
    words = text.split()
    if not words:
        return []

    step = chunk_size - overlap
    chunks = []
    start = 0
    while start < len(words):
        chunk_words = words[start : start + chunk_size]
        chunks.append(" ".join(chunk_words))
        if start + chunk_size >= len(words):
            break
        start += step
    return chunks
