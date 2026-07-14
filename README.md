# Epic Worlds Staff Assistant

A full-stack RAG-based conversational assistant for "Epic Worlds," a fictional theme park with
three themed areas (Future World, Adventure World, Fable World). Built as a portfolio project to
demonstrate agentic tool-calling, retrieval-augmented generation, and a structured-output API
contract shared between a Python backend and a Vue frontend.

Staff ask natural-language questions — attraction details, live wait times, accessibility,
tickets, events — and get back structured, card-based answers grounded in a markdown knowledge
base, not free text.

## Highlights

- **Agentic tool-calling, not a fixed pipeline.** The backend doesn't hardcode a
  retrieve-then-generate flow — Gemini decides itself whether, how many times, and in what order
  to call a knowledge-base search tool and a live-wait-times tool, via the `google-genai` SDK's
  Automatic Function Calling. See `docs/tech_spec.md` and `backend/CLAUDE.md` for the full
  three-phase orchestration flow (tool-use turn → routing → structured formatting turn).
- **Guardrailed retrieval.** A similarity-confidence threshold drops low-confidence knowledge-base
  matches before they ever reach the model, and out-of-scope or unanswerable questions route to a
  dedicated onboarding/guidance agent instead of a generic error.
- **Graceful degradation everywhere.** Every external call (Gemini, ChromaDB) is wrapped so
  failures surface as a specific, user-facing message rather than a raw error — including working
  around a subtle SDK behavior where tool-call exceptions don't propagate normally (see
  `backend/CLAUDE.md`, "Error handling").
- **Typed API contract.** Response cards are Pydantic models on the backend and a discriminated
  TypeScript union on the frontend, kept in sync by convention (`backend/models.py` ↔
  `frontend/src/types/index.ts`).

## Repository layout

```
themepark-assistant/
├── backend/     # FastAPI service (Python, uv) — RAG pipeline, orchestration, tools
├── frontend/    # Vue 3 + TypeScript chat UI
├── kb/          # Markdown knowledge base retrieved by the backend
└── docs/        # Technical/UI specs and phase-by-phase build log
```

## Running it locally

See `backend/README.md` and `frontend/README.md` for full setup. Short version:

```bash
# Backend
cd backend
uv sync
uv run python -m pipeline.indexer   # build the vector index (needs a GEMINI_API_KEY in .env)
uv run fastapi dev main.py          # http://localhost:8000

# Frontend, in a second terminal
cd frontend
npm install
npm run dev                         # http://localhost:5173
```

## Development process

This project was built incrementally through phased milestones, documented in `docs/phases/`
(skeleton → RAG pipeline → live ops & orchestration → polish/error handling). `docs/tech_spec.md`
and `docs/ui_spec.md` are the original design specs the implementation was driven from.

## Status

Live Ops (current wait times) is implemented but backed by mock data, not a real feed. Voice
input is unbuilt future work. Vector store and STT provider swaps (ChromaDB → Vertex AI Vector
Search) are wired for but not deployed — see `backend/README.md`.
