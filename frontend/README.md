# Frontend — Epic Worlds Staff Assistant

Vue 3 + TypeScript chat UI for the Epic Worlds Staff Assistant. Intentionally thin —
all retrieval, orchestration, and AI calls live in the sibling `../backend/` folder;
this app only captures input, calls `POST /query`, and renders the response as cards.

## Prerequisites

- Node 18+
- The backend running (see `../backend/README.md`)

## Setup

```bash
npm install
```

## Run

```bash
npm run dev
```

The dev server runs at `http://localhost:5173` and expects the backend at
`http://localhost:8000` by default.

## Pointing at a different backend

Copy `.env.example` to `.env.local` and set `VITE_API_BASE_URL` to the backend's
URL:

```
VITE_API_BASE_URL=http://localhost:8000
```

`.env.local` is gitignored, so this only affects your local machine.

## Type-check, build, lint

```bash
npm run build   # type-check + production build
npm run lint    # ESLint
```
