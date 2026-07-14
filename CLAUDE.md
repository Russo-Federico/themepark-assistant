# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A RAG-based conversational assistant for "Epic Worlds," a fictional theme park with three
themed areas (Future World, Adventure World, Fable World). The assistant answers guest/staff
questions (wait times, attraction details, accessibility, dining, tickets, etc.) grounded in
the knowledge base under `kb/`.

This is a single-repo portfolio consolidation of what was originally two separate projects
(`backend/` and `frontend/` here) — see `docs/phases/` for the original phased build log and
`docs/tech_spec.md`/`docs/ui_spec.md` for the original design specs. Each half still has its own
`CLAUDE.md` with implementation detail; this root file covers the whole-repo shape.

The backend has a fully working RAG pipeline: ChromaDB vector storage, Gemini for embeddings
and generation, and a `POST /query` endpoint backed by real agentic tool-calling. Live Ops
(current wait times) is implemented but backed by mock data (`backend/tools/live_ops_mock.py`),
not a real feed. There is no voice functionality yet; that's unbuilt future work.

## Repository layout

```
themepark-assistant/
├── backend/     # FastAPI service (Python, uv) — see backend/CLAUDE.md
├── frontend/    # Vue 3 + TypeScript chat UI — see frontend/CLAUDE.md
├── kb/          # Markdown knowledge base retrieved by the backend for RAG
└── docs/        # tech_spec.md, ui_spec.md, phases/phase_N.md (original build log)
```

`kb/` is organized by area (`park/`, `future_world/`, `adventure_world/`, `fable_world/`), with
each area containing an `*_area_guide.md`, an `*_accessibility.md`, and one file per attraction.
`backend/pipeline/indexer.py` resolves it as three directories up from itself
(`backend/pipeline/indexer.py` → `backend/` → repo root → `kb/`) — keep that relative depth if
either side ever moves.

**The API contract must stay in sync across both halves:** `ResponsePayload`/`Card` in
`backend/models.py` mirrors `ResponseCard` in `frontend/src/types/index.ts`. When adding/changing
a card shape, update both, plus the matching component in `frontend/src/components/cards/` and
the dispatch chain in `frontend/src/components/ChatFeed.vue`.

## Commands

```bash
# Backend (from backend/)
uv sync
uv run fastapi dev main.py         # dev server, http://localhost:8000
uv run python -m pipeline.indexer  # (re)build the ChromaDB index from kb/ — run before first use

# Frontend (from frontend/)
npm install
npm run dev                        # Vite dev server, http://localhost:5173
npm run build                      # type-check + production build
npm run lint                       # oxlint --fix, then eslint --fix --cache
```

A `GEMINI_API_KEY` must be set in `backend/.env` (loaded via `python-dotenv`) for both the indexer
and the server. The frontend reads `VITE_API_BASE_URL` (see `frontend/.env.example`) to locate the
backend, defaulting to `http://localhost:8000`.

There are currently no automated tests in either half.

## Architecture summaries

See `backend/CLAUDE.md` and `frontend/CLAUDE.md` for full detail. Briefly:

- **Backend query flow** (`backend/orchestrator.py`): not a fixed retrieve-then-generate
  pipeline — Gemini decides itself whether/how to call `search_knowledge_base` and
  `get_live_wait_times` via Automatic Function Calling, then a separate formatting turn produces
  structured cards via `response_schema`. A third, non-tool agent (`guide_tool.py`) handles
  out-of-scope or unanswerable questions.
- **Error handling**: every Gemini/ChromaDB call site returns a specific `FallbackCard` message on
  failure rather than a raw exception — including a workaround for Gemini's Automatic Function
  Calling swallowing tool-level exceptions internally (see `backend/CLAUDE.md`, "Error handling").
- **Frontend**: intentionally thin — no business logic, no prompt construction. `ChatFeed.vue`
  dispatches on `card_type` to one component per card type; Pinia (`stores/chat.ts`) is the only
  channel between sibling components.
- **Card styling** is split in two: `LiveOpsCard`/`AccessibilityCard`/`GuideCard` use a
  left-border accent system; `AttractionCard`/`EventCard` use a boxed shell with a header icon
  tile instead (icons are hardcoded per card type on the frontend, not sent by the backend).
