from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection

from config import CHROMA_PERSIST_PATH, VECTOR_STORE_PROVIDER

COLLECTION_NAME = "epic_worlds_kb"

BACKEND_DIR = Path(__file__).resolve().parents[1]

_collection: Collection | None = None


def _get_chromadb_collection() -> Collection:
    persist_path = BACKEND_DIR / CHROMA_PERSIST_PATH
    client = chromadb.PersistentClient(path=str(persist_path))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def _get_vertex_collection() -> Any:
    # Import deferred so flipping VECTOR_STORE_PROVIDER to "vertex_ai" never
    # breaks module import when google-cloud-aiplatform isn't installed. See
    # README.md "Vector store swap" for the setup steps to make this real.
    from google.cloud import aiplatform  # noqa: F401

    raise NotImplementedError(
        "Vertex AI Vector Search is not yet implemented. See backend/README.md "
        "'Vector store swap' for setup steps."
    )


def get_collection() -> Collection:
    global _collection
    if _collection is None:
        if VECTOR_STORE_PROVIDER == "vertex_ai":
            _collection = _get_vertex_collection()
        else:
            _collection = _get_chromadb_collection()
    return _collection
