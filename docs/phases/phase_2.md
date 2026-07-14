# Phase 2 — RAG Core

## Goal

Replace the mocked backend response with a real RAG pipeline. Text queries return real answers generated from the knowledge base. No agents, no orchestration, no voice — just straight retrieval and generation.

## Context

Phase 1 is complete. The frontend and backend are running and communicating. All card components exist as shells. The UI layout is finalised. The full technical spec is in `epic_worlds_tech_spec.md`.

## What Exists Already

- `backend/main.py` with a working `POST /query` endpoint returning a hardcoded mock
- `backend/config.py` with all config flags defined
- All frontend card components and ChatFeed wired up
- `kb/` folder with all 16 source documents

## What to Build

### Dependencies

Add to the backend via uv:

```bash
uv add chromadb google-genai fastmcp pydantic pypdf
```

(`google-generativeai` was the original package name planned here; the SDK was renamed to
`google-genai` before this was built, and that's what `pyproject.toml` actually uses.)

### Pydantic Response Models (`backend/models.py`)

Define one Pydantic model per card type matching the response contract in the tech spec, plus a `ResponsePayload` union model. These are passed to `response_schema` in the Gemini SDK call to enforce structured output.

### Update Pipeline (`backend/pipeline/`)

- `chunker.py` — splits `.md`, `.txt` files into overlapping text chunks (512 tokens, 50-token overlap). For `.pdf` files, extracts text via `pypdf` first, then chunks identically.
- `indexer.py` — recursive glob over `kb/` for `.md`, `.txt`, `.pdf` files. For each file: compute md5 hash, compare against `registry.json`, skip if unchanged, re-embed and upsert if changed or new, delete and remove if deleted. Reads metadata from file path (area from folder name, category from filename pattern).
- `registry.json` — created and maintained by the indexer. Stores `{ doc_id: { hash, last_updated, chunk_ids[] } }`.

Run the indexer once manually before starting the backend:

```bash
cd backend && uv run python -m pipeline.indexer
```

### Metadata Extraction

The indexer infers metadata from the file path:

- `area`: derived from the parent folder name (`future_world`, `adventure_world`, `fable_world`, `park` → `park_wide`)
- `category`: derived from filename patterns (`*_accessibility*` → `accessibility`, `*_tickets*` → `tickets`, `*_events*` → `events`, `*_area_guide*` → `area_guide`, everything else → `attractions`)
- `thrill_level`: extracted from document content for attraction files only (`1-2` → `low`, `3` → `moderate`, `4` → `high`, `5` → `very_high`)

### FastMCP Tool (`backend/tools/rag_tool.py`)

Implement `search_knowledge_base` as specified in the tech spec. Embeds the query with `gemini-embedding-2`, applies optional metadata filters, queries ChromaDB, returns top-K chunks with similarity scores. The Level 3 similarity threshold check (`SIMILARITY_THRESHOLD` from config) is enforced **inside this function** — chunks below the threshold are dropped before being returned to whatever calls it, rather than being checked by the caller afterwards. See "Orchestrator" below for why that matters.

### Orchestrator (`backend/orchestrator.py`)

> **Updated after initial build:** this phase originally shipped a fixed
> retrieve-then-generate pipeline (call `search_knowledge_base` once with the raw
> query → threshold check → splice chunks into the prompt → one generation call).
> It was refactored shortly after into true agentic tool-calling. The description
> below reflects the current implementation.

Two-phase generation — no manual retrieval step in the orchestrator itself:

1. Receive query + history, build `contents`.
2. **Phase A (tool-use turn):** call Gemini with `search_knowledge_base` exposed as a real tool via the SDK's Automatic Function Calling (capped at 3 tool round-trips). The model decides itself whether, how many times, and with what filters (`category`/`area`/`thrill_level`) to call it — e.g. two separate calls when comparing two attractions in one question. No `response_schema` on this call; the model must be free to emit a function call rather than be forced into JSON on every turn.
3. If the resulting tool-call transcript (`response.automatic_function_calling_history`) shows no call was made, or every call returned zero chunks, return `FallbackCard` directly — no further generation call needed.
4. **Phase B (formatting turn):** otherwise, replay that transcript plus a short formatting instruction into a second Gemini call — no tools this time, `response_schema=ResponsePayload` — to produce the final structured cards from what was already gathered.

Because the Level 3 threshold now lives inside `search_knowledge_base` itself (see above) rather than in the orchestrator, the guardrail applies automatically no matter how many times, or with what filters, the model calls the tool — the orchestrator doesn't need to re-check it.

### Update `backend/main.py`

Replace the hardcoded mock response with a call to the orchestrator.

### Guardrails Active in This Phase

- Level 1: system prompt (split across the tool-use and formatting phases, both carrying the same scope/grounding rule)
- Level 3: similarity threshold check, enforced inside `search_knowledge_base` rather than the orchestrator

## What NOT to Build in This Phase

- No STT or audio endpoint
- No intent classification
- No Live Ops tool or agent
- No hybrid query flow

## Exit Criteria

- Running the indexer with no errors populates ChromaDB with all 16 documents
- Running the indexer a second time with no KB changes skips all files (hashes match)
- Modifying one KB file and re-running the indexer re-embeds only that file
- Text query "what are the height requirements for Neon Circuit?" returns a real AttractionCard with correct data
- Text query "tell me a joke" returns a FallbackCard (out of scope, caught by Level 1)
- Text query completely unrelated to any KB content returns a FallbackCard (caught by Level 3)
- Gemini never returns free-text — all responses match the Pydantic schema
