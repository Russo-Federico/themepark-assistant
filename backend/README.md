# Backend — Epic Worlds Staff Assistant

FastAPI service implementing a RAG-based conversational assistant, backed by ChromaDB
for retrieval and Gemini for embeddings, tool-calling, and generation. See the repo
root `README.md` and `CLAUDE.md` for the full architecture.

## Prerequisites

- Python 3.12 (see `.python-version`)
- [`uv`](https://docs.astral.sh/uv/) for dependency and environment management
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

## Setup

```bash
cd backend
uv sync
```

Create `backend/.env` with:

```
GEMINI_API_KEY=your-key-here
```

## Build the index

Required before first use, and any time files under `kb/` change:

```bash
cd backend
uv run python -m pipeline.indexer
```

This embeds every knowledge base file into a local ChromaDB store at
`backend/chroma_db/` and records file hashes in `backend/pipeline/registry.json`
(both gitignored — a fresh clone starts with neither, so the indexer re-embeds
everything from scratch). Re-running it only re-embeds files that changed since
the last run.

## Run the server

```bash
cd backend
uv run fastapi dev main.py
```

The API is available at `http://localhost:8000`, exposing a single
`POST /query` endpoint: `{ "query": string, "history": [{ "role": string, "content": string }] }`.

## Configuration

All provider swaps live in `backend/config.py` — nothing else needs to change.

### Vector store swap (ChromaDB → Vertex AI Vector Search)

Set `VECTOR_STORE_PROVIDER = "vertex_ai"` in `config.py`. The code path exists in
`pipeline/vector_store.py` (`_get_vertex_collection`) so flipping the flag never
breaks module import, but the integration itself is a stub — it raises
`NotImplementedError` if actually reached. To make it real:

1. `uv add google-cloud-aiplatform`
2. Provision a Vertex AI Vector Search index and endpoint in your GCP project
3. Implement `_get_vertex_collection()` in `pipeline/vector_store.py` to return a
   client wrapping that index/endpoint, matching the same `query`/`upsert`/`delete`
   interface the indexer and `rag_tool.py` already call against the ChromaDB
   collection today
