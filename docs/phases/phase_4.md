# Phase 4 — Polish, Error Handling & Demo Readiness

## Goal

Harden the application for a real demo. Handle all error states gracefully. Verify config swaps. Write documentation. The project should be cloneable and runnable by someone unfamiliar with the codebase in under 10 minutes.

## Context

Phase 3 is complete. All features are functional: text input, RAG, Live Ops, intent classification, and the hybrid orchestration flow. This phase tightens everything up. The full technical spec is in `epic_worlds_tech_spec.md` and the UI spec is in `epic_worlds_ui_spec.md`.

Voice input is deferred (see `future_development.md`) — no STT/audio error handling in scope here.

## What Exists Already

- Full working application across all features
- All card components rendering correctly
- Both endpoints operational
- Update pipeline working

## What to Build

### Backend Error Handling

Wrap every failure point in a try/except and return a `FallbackCard` with an appropriate message rather than an HTTP 500. Specific cases to handle:

- Gemini API call fails or times out (Phase A tool-use turn, Phase B formatting turn, or the Guide agent's call) → FallbackCard: "The assistant is temporarily unavailable. Please try again."
- ChromaDB query fails (inside `search_knowledge_base`) → FallbackCard: "Could not search the knowledge base. Please try again."
- Phase A's tool-calling loop raises or exhausts its remote-call cap without a usable result → fall through to the Guide agent rather than failing entirely (same path as "no relevant tool results", see `phase_3.md`)

All errors should be logged to the console with enough detail to debug, but the response to the frontend is always a valid JSON FallbackCard — never a raw exception or HTTP error body.

### Frontend Error Handling

- Network request fails (backend unreachable) → render a FallbackCard inline in the chat: "Could not reach the assistant. Check your connection."
- Response JSON does not match any known `card_type` → render FallbackCard as a safe default
- Loading state: show animated pulsing dots in the ChatFeed between the user bubble and the arriving card. Remove dots when the card arrives.

### Edge Case Testing

Manually test and verify correct behaviour for:

- Out-of-scope query ("what is the capital of France?") → FallbackCard via Level 1 guardrail
- Query that matches no KB content ("who is the CEO of Epic Worlds?") → FallbackCard via Level 3 threshold
- Second query while first is still loading → disable send button during loading, re-enable on response
- Empty text field submission → prevent sending, no request fired

### Config Swap Verification

Verify and document the config swap works correctly:

**Vector store swap** — document the Vertex AI Vector Search setup steps in the README even if not deployed. The code path must exist in `rag_tool.py` without throwing import errors when the flag is set.

### README Files

Write a `README.md` for both `backend/` and `frontend/`. Each README must cover:

**Backend README:**
1. Prerequisites (Python 3.12, uv, a Gemini API key)
2. Setup: `uv sync`
3. Environment variables needed (`GEMINI_API_KEY`, in `backend/.env`)
4. How to run the indexer: `cd backend && uv run python -m pipeline.indexer`
5. How to start the server: `uv run fastapi dev main.py`
6. Config swap instructions for the vector store

**Frontend README:**
1. Prerequisites (Node 18+)
2. Setup: `npm install`
3. How to start: `npm run dev`
4. How to point at a different backend URL (env variable)

### Final UI Review

Do a pass against `epic_worlds_ui_spec.md` and verify:

- Card left border colors match the spec for LiveOpsCard, AccessibilityCard, and
  GuideCard. AttractionCard and EventCard were restyled to a boxed shell with a
  header icon tile instead (no left border) — verify against the current design,
  not the original left-border spec, for those two.
- Send button is disabled during loading
- `connector_label` renders correctly between LiveOpsCard and AttractionCards in hybrid responses
- FallbackCard renders cleanly for all error scenarios

(Dropped: "previous cards dim to 45% opacity" was never implemented and isn't part
of the current UI direction — out of scope going forward.)

## Exit Criteria

- Killing the backend while the frontend is running shows a graceful FallbackCard, not a broken UI
- All four edge cases listed above produce the correct graceful response
- A person unfamiliar with the project can clone the repo, follow the backend README, and have a working demo running in under 10 minutes
- `uv run python backend/pipeline/indexer.py` runs cleanly on a fresh clone with no existing `registry.json` or ChromaDB data
- The compound hybrid query demo scenario works reliably across at least 5 consecutive runs
