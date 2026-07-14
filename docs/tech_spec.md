# Epic Worlds Staff Assistant — Technical Specification

> This document describes the complete technical architecture, stack, and behaviour of the Epic Worlds Staff Assistant. It is intended as input for a vibe coding tool and should be treated as the single source of truth for all backend and frontend technical decisions.

---

## What the App Does

A staff-facing AI assistant for Epic Worlds theme park employees. It answers questions about attractions, tickets, events, accessibility, and live operational data. It accepts text and voice as input and returns structured card-based responses.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend language | Python |
| Package manager | uv |
| Agent framework | Google ADK (Agent Development Kit) |
| AI model (generation + orchestration) | `gemini-2.5-flash-lite` via Google AI Python SDK |
| Embeddings | `gemini-embedding-2` via Google AI Python SDK |
| Vector store | ChromaDB (local dev) → Vertex AI Vector Search (prod, one-line swap) |
| MCP tools | FastMCP (Python) |
| Speech to text | Whisper (local dev) → Google Cloud Speech-to-Text (prod, one-line swap) |
| API layer | FastAPI |
| Frontend | Vue 3 |
| Configuration | `config.yaml` (read at startup, no code changes needed to swap providers or models) |

---

## Project Structure

Two separate projects in one monorepo. They communicate exclusively over HTTP. Neither project has any knowledge of the other's internals.

```
epic-worlds-assistant/
│
├── backend/
│   ├── pyproject.toml           # uv project definition and dependencies
│   ├── uv.lock                  # exact pinned versions, committed to git
│   ├── config.yaml              # all runtime configuration — models, thresholds, providers
│   ├── config.py                # loads config.yaml into a typed Settings object at startup
│   ├── main.py                  # FastAPI app, all HTTP endpoints, CORS config
│   ├── agents/
│   │   ├── orchestrator.py      # ADK root agent — routes to sub-agents
│   │   ├── rag_agent.py         # ADK agent — owns search_knowledge_base tool
│   │   └── live_ops_agent.py    # ADK agent — owns get_live_wait_times tool
│   ├── tools/
│   │   ├── rag_tool.py          # search_knowledge_base FastMCP tool
│   │   └── live_ops_tool.py     # get_live_wait_times FastMCP tool
│   ├── pipeline/
│   │   ├── indexer.py           # reads /kb, embeds, stores in ChromaDB
│   │   ├── chunker.py           # splits .md, .txt, .pdf into chunks
│   │   └── registry.json        # hash registry for update pipeline
│   ├── stt/
│   │   └── transcriber.py       # Whisper / Google STT abstraction
│   └── models.py                # Pydantic response models for all card types
│
├── kb/                          # knowledge base source files (text only)
│   ├── park/
│   │   ├── epic_worlds_overview.md
│   │   ├── epic_worlds_tickets.md
│   │   └── epic_worlds_events_program.md
│   ├── future_world/
│   │   ├── future_world_area_guide.md
│   │   ├── future_world_accessibility.md
│   │   ├── orbit_station.md
│   │   ├── neon_circuit.md
│   │   └── data_dive.md
│   ├── adventure_world/
│   │   ├── adventure_world_area_guide.md
│   │   ├── adventure_world_accessibility.md
│   │   ├── thunder_rapids.md
│   │   ├── peak_assault.md
│   │   └── jungle_trek.md
│   └── fable_world/
│       ├── fable_world_area_guide.md
│       ├── fable_world_accessibility.md
│       └── dragon_flight.md
│
└── frontend/
    ├── package.json
    ├── src/
    │   ├── App.vue
    │   ├── components/
    │   │   ├── ChatFeed.vue
    │   │   ├── UserBubble.vue
    │   │   ├── InputBar.vue
    │   │   └── cards/
    │   │       ├── AttractionCard.vue
    │   │       ├── LiveOpsCard.vue
    │   │       ├── AccessibilityCard.vue
    │   │       ├── EventCard.vue
    │   │       └── FallbackCard.vue
    │   └── api/
    │       └── assistant.js     # all fetch calls to FastAPI
    └── ...
```

---

## Package Management (uv)

The backend uses **uv** for all dependency and environment management. Do not use pip directly.

```bash
# initialise the backend project
uv init backend
cd backend

# add dependencies
uv add fastapi uvicorn chromadb google-generativeai google-adk fastmcp openai-whisper pypdf pydantic pyyaml

# run the development server
uv run uvicorn main:app --reload
```

`uv.lock` must be committed to git. Anyone cloning the repo runs `uv sync` to get an identical environment — no manual venv activation required.

---

## Configuration

All runtime configuration lives in `config.yaml`. Think of it as the control panel for the application — every value that might need to change between environments, models, or providers is defined here. No Python code needs to be edited to swap a model or change a threshold.

### `config.yaml`

```yaml
# ── Models ────────────────────────────────────────────────────────────────────
models:
  gemini: "gemini-2.5-flash-lite"       # used for generation and ADK agents
  embedding: "gemini-embedding-2"        # used for indexing and query embedding

# ── Providers (swap here, no code changes needed) ─────────────────────────────
providers:
  vector_store: "chromadb"              # "chromadb" | "vertex_ai"
  stt: "whisper"                        # "whisper" | "google"

# ── RAG ───────────────────────────────────────────────────────────────────────
rag:
  retrieval_top_k: 5
  similarity_threshold: 0.70            # Level 3 guardrail — below this, return FallbackCard
  chunk_size: 512                       # tokens per chunk
  chunk_overlap: 50                     # overlapping tokens between chunks

# ── ChromaDB ──────────────────────────────────────────────────────────────────
chromadb:
  persist_path: "./chroma_db"
  collection_name: "epic_worlds_kb"

# ── Knowledge Base ────────────────────────────────────────────────────────────
kb:
  path: "../kb"
  supported_extensions: [".md", ".txt", ".pdf"]

# ── STT ───────────────────────────────────────────────────────────────────────
stt:
  whisper_model_size: "base"            # "tiny" | "base" | "small" | "medium" | "large"
  google_language_code: "en-US"

# ── API ───────────────────────────────────────────────────────────────────────
api:
  host: "0.0.0.0"
  port: 8000
  cors_origins: ["http://localhost:5173"]

# ── ADK Agents ────────────────────────────────────────────────────────────────
agents:
  max_tool_calls_per_turn: 5            # safety cap on ADK tool call loops
```

### `config.py`

Loads `config.yaml` at startup into a typed `Settings` object. All other Python modules import from `config.py` — they never read `config.yaml` directly.

```python
import yaml
from pydantic import BaseModel

class Settings(BaseModel):
    # typed fields mirroring config.yaml structure

def load_settings(path: str = "config.yaml") -> Settings:
    with open(path) as f:
        raw = yaml.safe_load(f)
    return Settings(**raw)

settings = load_settings()
```

All modules import the singleton: `from config import settings`

---

## Knowledge Base

### Supported File Types

`.md`, `.txt`, `.pdf`

PDF files have text extracted before chunking (via `pypdf`). After extraction, all file types flow through the same chunker and embedder.

### Source Documents

16 text files across 4 folders.

**Park-level (`/kb/park/`)**
- `epic_worlds_overview.md` — park intro, three areas at a glance, opening hours, facilities
- `epic_worlds_tickets.md` — all ticket tiers, pricing, validity, upgrades
- `epic_worlds_events_program.md` — seasonal events, daily entertainment schedules, character meet & greet times

**Future World (`/kb/future_world/`)**
- `future_world_area_guide.md` — area theme, atmosphere, dining, shopping, practical info
- `future_world_accessibility.md` — wheelchair routes, attraction-specific access, sensory info, companion pass
- `orbit_station.md` — attraction sheet
- `neon_circuit.md` — attraction sheet
- `data_dive.md` — attraction sheet

**Adventure World (`/kb/adventure_world/`)**
- `adventure_world_area_guide.md`
- `adventure_world_accessibility.md`
- `thunder_rapids.md` — attraction sheet
- `peak_assault.md` — attraction sheet
- `jungle_trek.md` — attraction sheet

**Fable World (`/kb/fable_world/`)**
- `fable_world_area_guide.md`
- `fable_world_accessibility.md`
- `dragon_flight.md` — attraction sheet

### Attraction Sheet Schema

Every attraction document contains these fields:

```markdown
| Field | Value |
|-------|-------|
| Area | Future World / Adventure World / Fable World |
| Manufacturer | ... |
| Thrill Level | 1–5 |
| Guests per Hour | ... |
| Height Requirement | ... cm / None |
| Duration | ... minutes |
| Type | e.g. launched coaster, indoor / dark ride, indoor |
| Express Pass | Yes / No |
```

Plus a **Story** section (2–3 lines of narrative) and an **Operational Notes** section.

---

## Embeddings and Vector Store

### Gemini Embedding 2

All KB content is embedded using the model specified in `config.yaml` under `models.embedding` at index time. The same model embeds the user query at query time. The same model must be used for both — mixing models breaks retrieval.

- Text chunks → embedded as text
- Audio → **never stored**. Voice queries are transcribed to text first, then embedded as text.

### ChromaDB

Stores all vectors with attached metadata. Each chunk is identified by `doc_id` + `chunk_index` as a composite primary key. Runs in-process with no external infrastructure during development.

**Config swap to prod:** set `providers.vector_store: "vertex_ai"` in `config.yaml`. No other changes needed.

### Metadata Schema

Every chunk stored in ChromaDB carries the following metadata:

```python
{
    "doc_id":        "thunder_rapids",
    "chunk_index":   0,
    "category":      "attractions",       # tickets | attractions | accessibility | events | area_guide
    "area":          "adventure_world",   # future_world | adventure_world | fable_world | park_wide
    "type":          "text",
    "thrill_level":  "high",              # low | moderate | high | very_high (attractions only)
    "last_updated":  "2025-06-13",
    "file_path":     "/kb/adventure_world/thunder_rapids.md"
}
```

Metadata filtering is applied before semantic search to scope results by `category` and/or `area`, reducing the search space and improving precision.

---

## Update Pipeline

Keeps ChromaDB in sync with `/kb` source files without re-indexing everything on every run.

### Hash-based change detection

```
for each file in /kb (recursive glob, extensions from config.yaml kb.supported_extensions):
    compute md5 hash of file contents
    compare against stored hash in registry.json

    if hash changed or file is new:
        delete existing chunks for this doc_id from ChromaDB
        extract text (PDF) or read directly (md, txt)
        re-chunk using chunk_size and chunk_overlap from config.yaml
        re-embed all chunks with model from config.yaml models.embedding
        upsert into ChromaDB
        update registry.json with new hash and chunk_ids[]

    if file was deleted:
        delete its chunks from ChromaDB
        remove entry from registry.json
```

`registry.json` structure:

```json
{
  "thunder_rapids": {
    "hash": "a3f5c2...",
    "last_updated": "2025-06-13",
    "chunk_ids": ["chunk_001", "chunk_002", "chunk_003"]
  }
}
```

`chunk_ids[]` is essential — it is the list of ChromaDB vector IDs belonging to this document, required to cleanly delete and reinsert when a file changes without leaving ghost chunks from old versions.

### Running the pipeline

Standalone script, run manually or on a schedule:

```bash
uv run python backend/pipeline/indexer.py
```

---

## Input Modalities

Two input types. All processing happens on the backend — the frontend captures and forwards, nothing more.

### Text

Employee types a question → sent as JSON string to `POST /query` → ADK orchestrator receives it directly.

### Voice

1. Vue captures audio via the browser `getUserMedia` API
2. Raw audio file sent to `POST /query/audio` as multipart form data
3. Backend transcribes via Whisper or Google Cloud STT (provider from `config.yaml`) → transcript string
4. Transcript treated identically to a text query from this point forward

**Config swap:** set `providers.stt: "google"` in `config.yaml`. No other changes needed.

---

## Backend Architecture

### FastAPI (`main.py`)

Thin HTTP layer. Exposes two endpoints:

```
POST /query          — body: { "query": string, "history": [...] }
POST /query/audio    — multipart: audio file + history as JSON field
```

Both endpoints return the same structured JSON response format. FastAPI validates the request, calls the ADK orchestrator, and returns the result. No business logic or AI logic lives in FastAPI.

CORS is configured from `config.yaml` under `api.cors_origins`.

### Session State

The frontend owns conversation history. Every request includes the full history of the current session. The backend is fully stateless — no session memory, no in-memory state per user.

Request payload shape:

```json
{
  "query": "Where can we redirect guests from Peak Assault?",
  "history": [
    { "role": "user",      "content": "What are the current wait times in Adventure World?" },
    { "role": "assistant", "content": "..." }
  ]
}
```

History exists for the current browser session only — it is not persisted anywhere.

---

## Agent Architecture (Google ADK)

Three ADK agents in a single Python process. Think of it like a specialist clinic: a receptionist (orchestrator) receives every patient and directs them to either the records department (RAG agent) or the monitoring station (Live Ops agent). The receptionist makes the routing decision; the specialists do the actual work.

### Orchestrator Agent (`agents/orchestrator.py`)

The root ADK agent. Has no tools of its own. Its only job is to classify the incoming query and delegate to the correct sub-agent.

```python
from google.adk.agents import LlmAgent

orchestrator = LlmAgent(
    name="orchestrator",
    model=settings.models.gemini,
    sub_agents=[rag_agent, live_ops_agent],
    instruction="""
    You are the orchestrator for the Epic Worlds Staff Assistant.
    Classify each incoming query and delegate to the appropriate sub-agent:
    - rag_agent: questions about attractions, tickets, events, accessibility, or park areas
    - live_ops_agent: questions about current wait times or real-time park status
    For questions requiring both (e.g. redirect suggestions based on current crowding),
    call live_ops_agent first, then pass the results to rag_agent for recommendations.
    Always respond with valid JSON matching the provided response schema.
    Never answer from your own knowledge — only from sub-agent results.
    """
)
```

### RAG Agent (`agents/rag_agent.py`)

Handles all static knowledge queries. Owns the `search_knowledge_base` tool.

```python
rag_agent = LlmAgent(
    name="rag_agent",
    model=settings.models.gemini,
    tools=[search_knowledge_base],
    instruction="""
    You answer questions about Epic Worlds using the search_knowledge_base tool.
    Only answer questions about attractions, tickets, events, themed areas, and accessibility.
    If the retrieved context does not contain enough information, return a fallback card.
    Never invent information not present in the retrieved chunks.
    """
)
```

### Live Ops Agent (`agents/live_ops_agent.py`)

Handles real-time operational data. Owns the `get_live_wait_times` tool.

```python
live_ops_agent = LlmAgent(
    name="live_ops_agent",
    model=settings.models.gemini,
    tools=[get_live_wait_times],
    instruction="""
    You provide real-time park operational data using the get_live_wait_times tool.
    Return current wait times clearly, categorised by area if requested.
    """
)
```

### FastMCP Tools

Two tools, each owned by one agent. Defined with FastMCP decorators and passed directly to the ADK agent constructors.

**`search_knowledge_base`** (owned by `rag_agent`)
```python
@mcp.tool()
def search_knowledge_base(
    query: str,
    category: str | None = None,    # optional metadata filter
    area: str | None = None,         # optional metadata filter
    thrill_level: str | None = None  # optional metadata filter
) -> list[dict]:
    # embeds query with model from config.yaml models.embedding
    # applies optional metadata filters in ChromaDB where clause
    # checks similarity threshold from config.yaml rag.similarity_threshold
    # returns top-K chunks (K from config.yaml rag.retrieval_top_k)
```

**`get_live_wait_times`** (owned by `live_ops_agent`)
```python
@mcp.tool()
def get_live_wait_times(
    area: str | None = None  # optional: filter by area
) -> list[dict]:
    # calls mock Live Ops module (real API integration in prod)
    # returns list of { attraction, area, wait_minutes }
```

### Guardrails

**Level 1 — Agent instructions (system prompt)**

Each agent's `instruction` field scopes its behaviour. The orchestrator is explicitly told never to answer from its own knowledge. The RAG agent is told never to invent information. This is the first line of defence against hallucination and out-of-scope responses.

**Level 3 — Retrieval confidence threshold**

Inside `search_knowledge_base`, after ChromaDB returns results, the top result's cosine similarity score is checked against `rag.similarity_threshold` from `config.yaml`. If below the threshold, the tool returns an empty result set rather than low-confidence chunks. The RAG agent then returns a fallback card. This guardrail applies only to vector retrieval — live ops queries are not affected.

### Structured Output Enforcement

The orchestrator calls Gemini with `response_schema` set to the `ResponsePayload` Pydantic model, enforcing that all responses match a known card schema before they leave the model:

```python
response = client.generate_content(
    contents=prompt,
    generation_config=genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=ResponsePayload
    )
)
```

### Example Compound (Hybrid) Query Flow

```
Query: "Where can we redirect guests from the most crowded rides?"

Orchestrator classifies → hybrid (needs both live data and KB knowledge)

Step 1 → delegates to live_ops_agent
  get_live_wait_times() → [Peak Assault: 85min, Neon Circuit: 70min, ...]

Step 2 → orchestrator passes live data context to rag_agent:
  "Crowded rides are high-thrill attractions in Adventure World and Future World.
   Find similar-thrill alternatives in other areas with low current wait."

Step 3 → rag_agent calls search_knowledge_base:
  query="high thrill indoor alternative attraction"
  area filter: NOT IN [adventure_world, future_world]
  → Dragon Flight, Orbit Station...

Step 4 → orchestrator generates structured multi-card JSON response
```

---

## Response Contract

All endpoints return the same JSON structure. A response is either a single card or a multi-card payload. The frontend renders components based on `card_type`. All responses are Pydantic-validated before being returned.

### Attraction card

```json
{
  "card_type": "attraction",
  "title": "Dragon Flight",
  "area": "Fable World",
  "subtitle": "similar thrill profile",
  "fields": [
    { "label": "Thrill level", "value": 3,               "type": "dots" },
    { "label": "Capacity",     "value": "2,400 guests/hr","type": "text" },
    { "label": "Current wait", "value": "12 min",        "type": "wait_badge", "level": "low" }
  ],
  "badges": ["accessible", "express_pass"],
  "footer": "Indoor flying theatre — high capacity makes it an effective load-balancer for Adventure World peaks."
}
```

### Live ops card

```json
{
  "card_type": "live_ops",
  "title": "Current Wait Times",
  "area": "Adventure World",
  "rows": [
    { "name": "Peak Assault",   "wait_minutes": 85, "level": "high" },
    { "name": "Thunder Rapids", "wait_minutes": 45, "level": "med"  },
    { "name": "Jungle Trek",    "wait_minutes": 10, "level": "low"  }
  ]
}
```

### Accessibility card

```json
{
  "card_type": "accessibility",
  "title": "Dragon Flight — Accessibility",
  "area": "Fable World",
  "fields": [
    { "label": "Wheelchair access", "value": "Transfer required", "type": "text" },
    { "label": "Companion pass",    "value": "Yes",               "type": "text" }
  ],
  "footer": "Transfer assistance provided by Storytellers at the boarding gate."
}
```

### Fallback card

```json
{
  "card_type": "fallback",
  "message": "I don't have reliable information on that. Please contact Guest Services or the relevant department."
}
```

### Multi-card response

```json
{
  "cards": [
    { "card_type": "live_ops",    "...": "..." },
    { "card_type": "attraction",  "...": "..." },
    { "card_type": "attraction",  "...": "..." }
  ],
  "connector_label": "Based on live data, suggested redirects:",
  "transcript": null
}
```

`connector_label` is rendered by the frontend as a visible text separator between the live ops card and the attraction cards. `transcript` is populated only for audio queries and is shown as the user bubble text.

---

## Frontend (Vue 3)

Intentionally thin. All intelligence lives in the backend.

### Responsibilities

- Capture text input and send to `POST /query`
- Capture audio via browser `getUserMedia` API, send raw file to `POST /query/audio`
- Maintain conversation history in component state, append to every request
- Render response JSON as the correct card component based on `card_type`
- Manage UI state: loading indicator, card history (previous cards dimmed to 45% opacity), mic recording state (pulse animation on mic button while recording)
- No business logic, no prompt construction, no AI calls

### Card Components

| `card_type` | Component |
|---|---|
| `attraction` | `AttractionCard.vue` |
| `live_ops` | `LiveOpsCard.vue` |
| `accessibility` | `AccessibilityCard.vue` |
| `event` | `EventCard.vue` |
| `fallback` | `FallbackCard.vue` |

`ChatFeed.vue` iterates over the `cards` array and renders the correct component for each entry. `connector_label` is rendered as a text separator between cards when present.

### InputBar Component

Two buttons, one text field (left to right):

1. **Mic button** — triggers `getUserMedia`, records audio, sends on second tap or silence detection. Pulses while recording.
2. **Text field** — standard input, sends on Enter or send button tap
3. **Send button** — submits current text input

Both buttons are disabled during loading. The send button is disabled when the text field is empty.

---

## What Is Not Included

- A2A protocol (all agents run in the same process — A2A adds no value here)
- Image as an input modality
- Image files in the knowledge base
- User authentication (assumed handled externally via SSO)
- Persistent conversation history across sessions
- Dark mode
- Real live ops API integration (mocked in dev)
- Video as an input or knowledge base modality
- Gemini Live (not needed — STT handles voice input sufficiently)
- LangChain or LlamaIndex (not needed — ADK + direct Google AI SDK calls throughout)
