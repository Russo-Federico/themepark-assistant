# Phase 1 — Skeleton & Sanity Check

## Goal

Verify that frontend and backend start up, communicate correctly, and that the UI layout feels right in the browser. No real AI features. All responses are hardcoded and mocked.

## Context

This is the first phase of an originally-planned 5-phase project. The full technical specification is in `epic_worlds_tech_spec.md`. The full UI specification is in `epic_worlds_ui_spec.md`. Read both before starting.

> **Note (added after the fact):** voice input, originally planned as its own phase, was deferred indefinitely (see `future_development.md`) — the project ultimately shipped as 4 phases (`phase_1.md`–`phase_4.md`), not 5.

## What Exists Already

Nothing. This phase builds the project from scratch.

## What to Build

### Backend

- Initialise the backend project using `uv init backend`
- Add dependencies: `fastapi`, `uvicorn`, `pydantic`
- Create `backend/config.py` with all configuration flags as specified in the tech spec (values do not need to be functional yet, just defined)
- Create `backend/main.py` with:
  - A single `POST /query` endpoint
  - CORS configured to allow `http://localhost:5173`
  - The endpoint accepts `{ "query": string, "history": [] }` and returns a single hardcoded `attraction` card JSON matching the response contract in the tech spec
  - No real logic — just return the static mock response every time

The hardcoded mock response to return:

```json
{
  "cards": [
    {
      "card_type": "attraction",
      "title": "Dragon Flight",
      "area": "Fable World",
      "subtitle": "mock response — phase 1",
      "fields": [
        { "label": "Thrill level", "value": 3, "type": "dots" },
        { "label": "Capacity", "value": "2,400 guests/hr", "type": "text" },
        { "label": "Current wait", "value": "12 min", "type": "wait_badge", "level": "low" }
      ],
      "badges": ["accessible", "express_pass"],
      "footer": "This is a mocked response. Real data will be wired in Phase 2."
    }
  ],
  "connector_label": null
}
```

### Frontend

- Scaffold the frontend using `npm create vue@latest frontend`
- Implement the full UI layout as specified in `epic_worlds_ui_spec.md`:
  - Header with logo, app name, live status dot
  - ChatFeed area (scrollable)
  - InputBar with mic button (left), text field (center), send button (right)
- Implement all card components as shells that correctly render their respective JSON shapes:
  - `AttractionCard.vue`
  - `LiveOpsCard.vue`
  - `AccessibilityCard.vue`
  - `EventCard.vue`
  - `FallbackCard.vue`
- `ChatFeed.vue` iterates over the `cards` array in the response and renders the correct component based on `card_type`
- `UserBubble.vue` renders the employee's query as a right-aligned bubble in the brand accent color
- `assistant.ts` contains the fetch call to `POST /query` at `http://localhost:8000`
- Conversation history maintained in Vue component state and appended to every request
- Previous cards dimmed to 45% opacity when a new response arrives (**note added after the fact:**
  this was never actually implemented and was dropped from scope entirely in `phase_4.md`'s final
  UI review — don't treat it as a real feature)
- Mic button is visible and correctly styled but does not record yet — clicking it does nothing in this phase

## What NOT to Build in This Phase

- No Whisper or STT of any kind
- No ChromaDB, no embeddings, no Gemini calls
- No update pipeline
- No FastMCP tools
- No intent classification
- No `POST /query/audio` endpoint

## Exit Criteria

- `uv run uvicorn main:app --reload` starts the backend with no errors
- `npm run dev` starts the frontend with no errors
- Typing a question in the text field and pressing send renders a Dragon Flight attraction card in the UI
- The user's question appears as an accent-colored bubble above the card
- On a second query, the first card dims to 45% opacity (**note added after the fact:** this was
  never built — see the note above; treat this bullet as historical intent, not an achieved result)
- All five card component shells exist and accept their respective JSON shapes without errors
