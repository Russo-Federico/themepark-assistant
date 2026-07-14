# Phase 3 — Live Ops Agent + Orchestration

## Goal

Add the Live Ops agent and wire up the full hybrid query flow. The compound scenario — live wait times followed by RAG-based redirect suggestions — works end to end. Also add a Guide agent so that greetings, meta questions ("what can you help with?"), and low-confidence knowledge queries get a helpful, dynamic response instead of a generic fallback.

## Context

Phase 2 is complete, and was refactored after its initial build to use true agentic tool-calling instead of a fixed pipeline — see the "Orchestrator" section of `phase_2.md`. `handle_query` already runs a **Phase A tool-use turn** (Gemini decides itself whether/how many times/with what filters to call `search_knowledge_base`, via the SDK's Automatic Function Calling) followed by a **Phase B formatting turn** (no tools, `response_schema=ResponsePayload`) once the model has gathered what it needs.

> **Updated from the original plan:** this phase originally called for a separate intent-classification step (a dedicated `gemini-2.5-flash-lite` call returning `knowledge`/`live_ops`/`hybrid`/`guide`) with hardcoded `if/else` routing in the orchestrator. That design predates the Phase 2 agentic refactor and now conflicts with it — a second classifier call re-introduces exactly the kind of fixed, non-agentic routing the refactor removed. This version instead adds `get_live_wait_times` as a **second tool in the same Phase A loop** and lets the model decide which tool(s) to call, the same way it already decides how many times to call `search_knowledge_base`. No classifier call, no hardcoded routing.

The full technical spec is in `epic_worlds_tech_spec.md`. Voice input (originally scoped as Phase 3) has been deferred — see `future_development.md`. This phase does not depend on it.

## What Exists Already

- Full RAG pipeline with agentic tool-calling (`search_knowledge_base` as a Phase A tool, `orchestrator.handle_query` doing Phase A → Phase B)
- `POST /query` endpoint
- All card components including `LiveOpsCard.vue`
- `config.py` with all flags defined

## What to Build

### Mock Live Ops API (`backend/tools/live_ops_mock.py`)

Unchanged from the original plan: a simple in-memory mock returning realistic fake wait times for all attractions, as a list of `{ attraction, area, wait_minutes }` dicts, varied enough to make the hybrid scenario interesting across all three areas. Plain Python module, not a real HTTP server.

### Second Phase A Tool (`backend/tools/live_ops_tool.py`)

Implement `get_live_wait_times(area: str | None = None) -> list[dict]`, calling the mock module and optionally filtering by area. Follow the same convention just established for `search_knowledge_base` in Phase 2: a rich docstring (overall description + an `Args:` section spelling out valid `area` values) since that docstring is what the model reads to decide when and how to call it — there is no separate classifier prompt telling it when this tool applies. No `SIMILARITY_THRESHOLD` filtering applies here — that guardrail is specific to `search_knowledge_base`'s retrieval results, not to live operational data, so it's correctly bypassed simply by not being in this function at all (no special-casing needed in the orchestrator, unlike the original plan which had to explicitly carve out an exception for `live_ops` intent).

### Orchestrator Changes (`backend/orchestrator.py`)

- Add `get_live_wait_times` alongside `search_knowledge_base` in Phase A's `tools=[...]` list.
- Update `TOOL_SYSTEM_PROMPT` to describe both tools and give the model the hybrid reasoning pattern directly, e.g.: "If asked where to redirect guests from crowded attractions, first check live wait times, identify the most crowded ones, then look up suitable alternatives elsewhere in the park (different area, similar or lower thrill level) using `search_knowledge_base`." The model chains the two tool calls itself — there is no separate hardcoded "hybrid flow" function building an enriched query or an area-exclusion filter; that reasoning happens inside the model's own tool-calling turn, informed by the system prompt.
- The existing "no tool call, or every call returned nothing useful" fallback check now needs to account for both tools: if neither tool was called, or every call across both returned an empty result, treat it as the fallback case. This single condition now covers what used to be three separate cases (`guide` intent directly, `knowledge` failing Level 3, `hybrid` failing Level 3) — see "Guide Agent" below.
- Phase B's formatting prompt needs to handle transcripts containing a live-ops result, a knowledge result, or both: produce a `LiveOpsCard`, one or more `AttractionCard`s, or both together with `connector_label` populated when both are present.

### Guide Agent (Onboarding Assistance)

Unchanged in behavior from the original plan, simplified in how it's reached. Implement `backend/tools/guide_tool.py` exposing `generate_guide_response(query: str, history: list) -> dict` — a **second, separate** `gemini-2.5-flash-lite` call (not Phase A, not Phase B) with its own system prompt:

```
You are the onboarding guide for the Epic Worlds Staff Assistant. You are NOT
answering questions about the park — you help staff understand what this
assistant can do and how to ask it better questions.

The assistant can help with:
- Attraction details (thrill level, capacity, wait times) across Future World,
  Adventure World, and Fable World
- Accessibility information per attraction and per area
- Dining and shopping locations
- Tickets and events
- Live operational data (current wait times, crowding)

You do NOT have retrieved knowledge base content for this turn. Never state
specific facts about attractions, wait times, or accessibility. If the user's
question sounds like a genuine park question you don't have context for,
acknowledge that and suggest how to rephrase it — do not attempt to answer it.

Query: {query}
```

Call this whenever Phase A's tool-call transcript has no calls, or only calls that returned empty results — that single condition is reached identically whether the query was a plain greeting (the model had no reason to call anything) or a genuine park question with no matching data (the model tried a tool and got nothing back). No classification step is needed to tell those two cases apart before routing to the Guide agent, since both already collapse to the same observable signal in the transcript.

Feed the model only the static list of KB categories/areas (pull this from `config.py` or a small manifest — never the retrieved chunk text, and never call `search_knowledge_base` from this path). Keeping its grounding scope limited to "what the app can do" — never "what is true about the park" — means this path carries none of the Level 1/Level 3 hallucination risk that the grounded tool-calling path guards against.

The response should include 2–3 example questions tailored to the user's query when possible (e.g. if the query mentioned "accessibility" but matched nothing, suggest rephrased accessibility questions), and always fall back to generic category examples if no signal can be extracted from the query.

### Update Response Models (`backend/models.py`)

Ensure `LiveOpsCard` Pydantic model is defined and included in the `ResponsePayload` union. `connector_label` must be populated for multi-card hybrid responses.

Add a `GuideCard` Pydantic model to the same union, with fields `message: str` and `example_questions: list[str]`.

### Frontend — `ChatFeed.vue`

Ensure the `connector_label` is rendered as a visible text separator between the LiveOpsCard and the subsequent AttractionCards. This should already work if `ChatFeed.vue` handles the `connector_label` field from Phase 1, but verify and fix if needed.

### Frontend — `GuideCard.vue`

Add a new card component, following the same conventions as the other card shells from Phase 1 (left border color per `epic_worlds_ui_spec.md`). Renders the `message` text plus the `example_questions` as clickable chips — clicking one fills the input bar with that question (does not auto-send). Wire `card_type: "guide"` into `ChatFeed.vue`'s existing component switch.

## What NOT to Build in This Phase

- No real live ops API integration (mock only)
- No error handling polish (that is Phase 4)
- No separate intent-classification call and no hardcoded knowledge/live_ops/hybrid routing function — that responsibility now belongs entirely to the model's own tool selection in Phase A
- No factual claims about attractions, wait times, or accessibility from the Guide agent — it only describes app scope and suggests rephrasing, it never answers the underlying park question
- No retrieved KB content or `search_knowledge_base` calls feeding into the Guide agent's prompt

## Exit Criteria

- Query "what are the current wait times in Adventure World?" returns a LiveOpsCard with color-coded wait badges (the model calls only `get_live_wait_times`, no `search_knowledge_base` call in the transcript)
- Query "tell me about Dragon Flight" returns an AttractionCard (the model calls only `search_knowledge_base`, no live ops call)
- Query "where can we redirect guests from the most crowded rides?" returns a LiveOpsCard followed by one or more AttractionCards with `connector_label` rendered between them (the model calls both tools within the same Phase A turn, without any hardcoded hybrid-flow function driving it)
- Across repeated testing, the model reliably picks the right tool(s) for each of the three cases above with no classifier in the loop
- Query "ciao" / "what can you help me with?" returns a GuideCard explaining the assistant's scope with example questions, not a generic FallbackCard
- Query "who is the CEO of Epic Worlds?" (real question, no matching data, all tool calls return empty) returns a GuideCard suggesting how to rephrase, not a generic FallbackCard
- Across repeated testing with ambiguous queries, the Guide agent never asserts a specific fact about an attraction, wait time, or accessibility detail — it only describes scope or suggests rephrasing
