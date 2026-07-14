# backend/CLAUDE.md

Backend-specific guidance. See the repo root `CLAUDE.md` for the whole-project shape.

## Commands

All commands run from `backend/` using `uv` (Python 3.12, per `.python-version`).

```bash
uv sync                            # install/sync dependencies from uv.lock
uv run fastapi dev main.py         # run the dev server with reload (http://localhost:8000)
# or: uv run uvicorn main:app --reload
uv run python -m pipeline.indexer  # (re)build the ChromaDB index from ../kb — run before first use
```

A `GEMINI_API_KEY` must be set (e.g. in `backend/.env`, loaded via `python-dotenv`) for both the
indexer and the server, since both call the Gemini API.

There are currently no tests or lint configuration in this project.

## Architecture

- `config.py` is the single switchboard for provider choices (vector store, STT, models, RAG
  parameters, CORS origin). **All provider swaps should be made here, not scattered across other
  files.** Read the active value from this file rather than hardcoding a provider.
- `main.py` — FastAPI app; the `POST /query` endpoint is a thin wrapper around
  `orchestrator.handle_query`. The response shape (`cards` with `card_type`, `fields`, `badges`,
  `connector_label`, etc., defined in `models.py`) is the contract the frontend renders against —
  preserve it when touching the orchestrator. `models.py` defines one `BaseModel` per card type
  (`AttractionCard`, `LiveOpsCard`, `AccessibilityCard`, `EventCard`, `GuideCard`, `FallbackCard`),
  unioned into `Card`, plus the top-level `ResponsePayload` (`cards` + optional `connector_label`)
  that Phase B's `response_schema` targets. `FieldItem.type` is
  `"text" | "dots" | "wait_badge" | "number"` — `"number"` renders as a large stat with the unit
  written inline in the value string (e.g. `"2,400 guests / hr"`), used by `AttractionCard`'s
  boxed icon-tile layout. `EventCard` does **not** use `fields` — it has a plain `description: str`
  for prose (event content in `kb/` is narrative, not label/value stats) plus an optional `footer`
  for guest restrictions/add-on costs.
- `main.py` also registers a catch-all `@app.exception_handler(Exception)` that returns a 500 with
  a generic `FallbackCard` JSON body (needed so the response still carries CORS headers — see the
  comment in `main.py`). This is a **last-resort** safety net only, for genuinely unanticipated
  bugs — the expected failure points (Gemini calls, ChromaDB queries) are caught individually
  inside `orchestrator.py`/`tools/rag_tool.py`/`tools/guide_tool.py` and always return 200 with a
  specific `FallbackCard` message; see "Error handling" below.

### Indexing (`pipeline/`)

- `chunker.py` extracts text (`.md`/`.txt` read directly, `.pdf` via `pypdf`) and splits it into
  overlapping word-count windows (`CHUNK_SIZE_TOKENS`/`CHUNK_OVERLAP_TOKENS` from config — a
  word-based approximation, not a real tokenizer). No structural (markdown header/table)
  awareness; every current `../kb/` file is under the chunk size, so today each document is a
  single chunk in practice.
- `indexer.py` (`run_indexer`, invoked as a standalone script, not from the API) walks `../kb/`,
  skips unchanged files via an MD5 hash tracked in `pipeline/registry.json`, infers metadata
  per file (`area` from folder, `category` from filename pattern, `thrill_level` regexed from
  attraction pages), embeds new/changed chunks via `genai_client.embed_documents`, and
  upserts/deletes in ChromaDB accordingly. `pipeline/registry.json` (like `chroma_db/`) is
  gitignored, not committed — a fresh clone has neither, so the first indexer run always
  re-embeds everything from scratch rather than trusting a stale registry.
- `vector_store.py` — `get_collection()` is the single place a vector store client is
  instantiated, cached in a module-level singleton after first call. It branches on
  `config.VECTOR_STORE_PROVIDER`: `"chromadb"` (default) goes through `_get_chromadb_collection()`
  (a `PersistentClient` at `CHROMA_PERSIST_PATH`, collection `epic_worlds_kb`, cosine similarity);
  `"vertex_ai"` goes through `_get_vertex_collection()`, a documented stub — its Vertex import is
  deferred inside the function body specifically so flipping the flag never breaks module import,
  but it raises `NotImplementedError` if actually reached (see `README.md` for what implementing
  it for real would involve).

### Query flow — agentic tool-calling (`orchestrator.py`)

`handle_query` is **not** a fixed retrieve-then-generate pipeline — it lets Gemini decide if/how
to retrieve, via the `google-genai` SDK's Automatic Function Calling (AFC). Three separate LLM
"agents" are involved, only the first of which has tools:

1. **Phase A (tool-use turn):** call `generate_content` with two real tools exposed
   (`AutomaticFunctionCallingConfig(maximum_remote_calls=3)`), no `response_schema` — the model
   decides whether, how many times, in what order, and with what filters to call them:
   - `tools/rag_tool.search_knowledge_base` — vector search over `../kb/`, optionally filtered by
     `category`/`area`/`thrill_level` (e.g. two calls when comparing two attractions).
   - `tools/live_ops_tool.get_live_wait_times` — current wait times, backed by the in-memory mock
     data in `tools/live_ops_mock.py`, optionally filtered by `area`.
   The system prompt (`TOOL_SYSTEM_PROMPT`) tells the model to call `get_live_wait_times` before
   `search_knowledge_base` on hybrid questions (e.g. "where should I redirect guests from a
   crowded attraction?"), since tool call order drives the order info appears in the final answer.
2. **Routing:** `_found_relevant_results` inspects `response.automatic_function_calling_history`.
   If no tool was called, or every call returned nothing, control passes to a **second agent**,
   `tools/guide_tool.generate_guide_response` — not a tool the model can call, but a plain Python
   function invoked directly by the orchestrator. It's a separate `generate_content` call with
   its own system prompt and `response_schema=GuideCard`: an onboarding/guidance agent that never
   states park facts, it only teaches staff how to phrase a better question.
3. **Phase B (formatting turn), third agent:** otherwise, replay the Phase A transcript into a
   new `generate_content` call with no tools but `response_mime_type="application/json"` +
   `response_schema=ResponsePayload`, to produce the final structured cards from what was already
   gathered. `FORMAT_SYSTEM_PROMPT` covers three shapes: live-ops-only (one `LiveOpsCard`,
   bucketing raw `wait_minutes` into low/med/high), KB-only (one or more KB-grounded cards), or
   both (`LiveOpsCard` first, then KB card(s), with `connector_label` explaining the relationship).

The Level 3 similarity-confidence guardrail (`SIMILARITY_THRESHOLD`) is enforced **inside**
`tools/rag_tool.search_knowledge_base` itself (chunks below threshold are dropped before ever
reaching the model), not in the orchestrator — this way it applies no matter how many times or
with what filters the model calls the tool. Both `search_knowledge_base` and
`get_live_wait_times` are also decorated as FastMCP tools (`@mcp.tool()`, on two separate
`FastMCP` instances), but that decorator returns the plain function unchanged, so they're
imported and used directly as Python callables both by the orchestrator and (potentially) MCP
clients.

### Error handling

Every Gemini call site in the query path (Phase A, Phase B, and the Guide agent's own call) is
wrapped in try/except, returning a `FallbackCard` with a specific message rather than letting an
exception reach `main.py`'s catch-all. `search_knowledge_base` (`tools/rag_tool.py`) raises a
`KnowledgeBaseUnavailableError` on a ChromaDB failure instead of returning `[]`, so a broken vector
store isn't silently indistinguishable from "no matching chunks."

**Gotcha:** the `google-genai` SDK's Automatic Function Calling catches exceptions raised *inside*
tool functions itself and never lets them propagate to the `generate_content()` call site — it
converts them into a `function_response` with an `{"error": "..."}` payload instead, and the model
just tries something else. This means `KnowledgeBaseUnavailableError` can **not** be caught with a
try/except around Phase A's `generate_content` call (that only catches genuine Gemini-level
failures, e.g. after `genai_client`'s retries are exhausted). Detecting a ChromaDB failure requires
inspecting `tool_response.automatic_function_calling_history` after the call for a
`search_knowledge_base` response containing an `"error"` key (`orchestrator._kb_search_failed`) —
and only short-circuiting to the KB-specific fallback when *nothing else* in the same turn
succeeded either (e.g. a hybrid query where live ops still returned data should still produce a
normal response, not a blanket failure).

### Gemini access (`genai_client.py`)

Single choke point for the Gemini client (cached singleton, like `vector_store.get_collection()`).
Exposes `embed_documents`, `embed_query`, and `generate_content` — all three go through an
internal `_with_retry` helper that retries on `ServerError` (5xx) or `ClientError` with code 429,
with capped exponential backoff; other 4xx errors fail immediately. Always call these wrappers
rather than `client.models.*` directly, so retry behavior stays consistent.
