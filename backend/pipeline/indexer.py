import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from genai_client import embed_documents  # noqa: E402
from pipeline.chunker import chunk_text, extract_text  # noqa: E402
from pipeline.vector_store import get_collection  # noqa: E402

KB_ROOT = Path(__file__).resolve().parents[2] / "kb"
REGISTRY_PATH = Path(__file__).resolve().parent / "registry.json"

KB_EXTENSIONS = ("*.md", "*.txt", "*.pdf")

THRILL_LEVEL_MAP = {
    1: "low",
    2: "low",
    3: "moderate",
    4: "high",
    5: "very_high",
}

THRILL_LEVEL_PATTERN = re.compile(r"thrill level\*\*\s*\|\s*(\d)\s*/\s*5", re.IGNORECASE)


def load_registry() -> dict:
    if REGISTRY_PATH.exists():
        return json.loads(REGISTRY_PATH.read_text())
    return {}


def save_registry(registry: dict) -> None:
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2))


def compute_md5(file_path: Path) -> str:
    return hashlib.md5(file_path.read_bytes()).hexdigest()


def infer_area(file_path: Path) -> str:
    folder = file_path.parent.name
    return "park_wide" if folder == "park" else folder


def infer_category(file_path: Path) -> str:
    stem = file_path.stem.lower()
    if "accessibility" in stem:
        return "accessibility"
    if "tickets" in stem:
        return "tickets"
    if "events" in stem:
        return "events"
    if "area_guide" in stem:
        return "area_guide"
    return "attractions"


def infer_thrill_level(text: str) -> str | None:
    match = THRILL_LEVEL_PATTERN.search(text)
    if not match:
        return None
    return THRILL_LEVEL_MAP[int(match.group(1))]


def build_metadata(file_path: Path, chunk_index: int, category: str, area: str, thrill_level: str | None, last_updated: str) -> dict:
    return {
        "doc_id": file_path.stem,
        "chunk_index": chunk_index,
        "category": category,
        "area": area,
        "type": "text",
        "thrill_level": thrill_level or "",
        "last_updated": last_updated,
        "file_path": f"/kb/{file_path.parent.name}/{file_path.name}",
    }


def run_indexer() -> None:
    registry = load_registry()
    collection = get_collection()

    files = sorted(
        path for pattern in KB_EXTENSIONS for path in KB_ROOT.rglob(pattern)
    )
    seen_doc_ids = set()

    for file_path in files:
        doc_id = file_path.stem
        seen_doc_ids.add(doc_id)

        file_hash = compute_md5(file_path)
        existing = registry.get(doc_id)
        if existing and existing["hash"] == file_hash:
            print(f"skip  {doc_id} (unchanged)")
            continue

        if existing:
            collection.delete(ids=existing["chunk_ids"])

        text = extract_text(file_path)
        chunks = chunk_text(text)
        if not chunks:
            print(f"skip  {doc_id} (no extractable text)")
            registry.pop(doc_id, None)
            continue

        category = infer_category(file_path)
        area = infer_area(file_path)
        thrill_level = infer_thrill_level(text) if category == "attractions" else None
        last_updated = date.fromtimestamp(file_path.stat().st_mtime).isoformat()

        chunk_ids = [f"{doc_id}::{i}" for i in range(len(chunks))]
        embeddings = embed_documents(chunks)
        metadatas = [
            build_metadata(file_path, i, category, area, thrill_level, last_updated)
            for i in range(len(chunks))
        ]

        collection.upsert(ids=chunk_ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
        registry[doc_id] = {"hash": file_hash, "last_updated": last_updated, "chunk_ids": chunk_ids}
        print(f"index {doc_id} ({len(chunks)} chunks)")

    for doc_id in list(registry.keys()):
        if doc_id not in seen_doc_ids:
            collection.delete(ids=registry[doc_id]["chunk_ids"])
            del registry[doc_id]
            print(f"remove {doc_id} (deleted from kb/)")

    save_registry(registry)


if __name__ == "__main__":
    run_indexer()
