# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Vue 3 + TypeScript frontend for the Epic Worlds Staff Assistant — an internal chat tool that lets
theme park employees ask questions (attraction details, wait times, accessibility, dining, tickets)
and get back structured, card-based answers instead of free text.

This is one half of a single-repo project — see the root `CLAUDE.md` for the whole-project shape.
Reference docs (not code, don't treat as source of truth over what's actually implemented — they
can drift) live at the repo root:
- `../docs/tech_spec.md` — full system spec (backend + frontend + API contract)
- `../docs/ui_spec.md` — visual design spec (colors, typography, card layout)
- `../docs/phases/phase_N.md` — the phase-by-phase build log this was originally driven from
- `../kb/` — the markdown knowledge base the backend retrieves from (read-only reference; not consumed by the frontend)

## Commands

```sh
npm install          # install dependencies
npm run dev          # start Vite dev server
npm run build         # type-check + production build
npm run type-check    # vue-tsc --build (no separate test suite exists in this repo)
npm run lint          # oxlint --fix, then eslint --fix --cache
npm run format        # prettier --write src/
```

There is no test runner configured (no vitest/jest in package.json); `src/**/__tests__/*` is
excluded from `tsconfig.app.json` in anticipation of one but none exists yet.

## Backend

The backend lives in the sibling `../backend/` folder (FastAPI + Python, managed with `uv`). It is
a real, working service — not a stub.

- Do **not** create a mock/fake backend server to test FE changes.
- To verify FE work against real data, run the actual backend:
  ```bash
  cd ../backend
  uv sync
  uv run fastapi dev main.py
  ```
  It serves `POST /query` on `http://localhost:8000` by default — `src/api/assistant.ts` reads
  `import.meta.env.VITE_API_BASE_URL` (falling back to that default), so pointing at a different
  backend is a `.env.local` change (see `.env.example`), not a code change.
- If the real backend can't be reached and a mock is genuinely the only option, ask first rather
  than doing it silently.

## Architecture

**Single-route SPA.** `router/index.ts` only maps `/` to `ChatView.vue`, which just renders
`ChatFeed`. Almost all real UI lives in `App.vue`'s always-mounted siblings: `AppHeader`,
`ChatFeed`, `InputBar`, `SettingsPanel` (toggled in/out via `v-if`), `ToastNotification`.

**Pinia is the only channel between siblings.** `ChatFeed`, `InputBar`, and `AppHeader` are
siblings under `App.vue`, not parent/child, so any state one needs to affect in another goes
through `useChatStore` (`src/stores/chat.ts`) rather than props/emits — e.g. `isScrolled` (feed
scroll position → header zero-UI behavior), `isSettingsOpen`, and `draftQuery` (a card's example
question chip → fills the input bar without sending). Card components themselves are pure/dumb:
they take a typed `card` prop and emit events, they don't import the store directly.

**API contract lives in two places that must stay in sync:** `src/api/assistant.ts` (the fetch
call to `POST /query`) and `src/types/index.ts` (the `ResponseCard` discriminated union, keyed on
`card_type`). Each variant in the union corresponds 1:1 with a Pydantic model on the backend
(`AttractionCard`, `LiveOpsCard`, `AccessibilityCard`, `EventCard`, `GuideCard`, `FallbackCard`).
When the backend adds/changes a card shape, both files need updating here. Note `EventCard` has no
`fields` array (unlike `AttractionCard`/`AccessibilityCard`) — it's a plain `description: string`
for prose plus an optional `footer`, matching event content in the backend's `kb/` being narrative
rather than label/value stats.

**`assistant.ts` trusts the backend's error contract; don't re-introduce a blanket throw-on-!res.ok.**
`postQuery` reads the JSON body regardless of HTTP status, because the backend guarantees a valid
`FallbackCard` body even on a 500 for its own handled failures — only a genuine `fetch()`-level
failure (connection refused) or an unparseable/malformed body (`MalformedResponseError`) should
produce the frontend's own generic messages. `stores/chat.ts`'s `sendMessage` branches on which of
those it was to pick the right message, and separately validates every incoming card's `card_type`
against a hardcoded `KNOWN_CARD_TYPES` list before rendering — **remember to add a new card type
to that list** (alongside the union in `types/index.ts` and the dispatch chain in `ChatFeed.vue`
described below), or it'll silently get replaced with a fallback card at render time.

**Card rendering dispatch happens in one place:** `ChatFeed.vue` has a `v-for` over `msg.cards`
with a `v-if`/`v-else-if` chain on `card.card_type` that picks the matching component from
`src/components/cards/`. Adding a new card type means: extend the union in `types/index.ts`, add
the component, wire it into this chain. `connector_label` (a text separator between card groups)
is rendered by `ChatFeed` at the boundary right after a leading run of `live_ops` cards, not simply
above the whole card list — this matters for hybrid responses (live wait times followed by
redirect suggestions).

**Styling is CSS custom properties**, defined once in `src/assets/styles/variables.css` and
consumed via `var(--token-name)` in each component's `<style scoped>` block — there's no CSS
framework. Note the shipped dark theme's actual hex values diverge from the light palette
described in `../docs/ui_spec.md`, and the card system itself has since split in two:
`LiveOpsCard`/`AccessibilityCard`/`GuideCard` still use the original left-border-per-card-type
accent system (`--color-accent-liveops`/`-accessibility`/`-guide`); `AttractionCard`/`EventCard`
were restyled to a boxed shell (background + full border + radius) with a 32×32px header icon
tile instead (`--color-icon-attraction-bg/fg`, `--color-icon-event-bg/fg` — a hardcoded emoji per
card type, not data from the backend). Treat `../docs/ui_spec.md` as describing the
left-border cards only now; don't "fix" Attraction/Event back to match it. Each card type owns its
own `.card` styles independently (no shared base card component/mixin) — new cards should follow
whichever of the two existing patterns fits, rather than introduce shared abstractions.

**`useToast` (`src/composables/useToast.ts`) is a module-level singleton, not a Pinia store** —
`toasts` is a module-scoped `ref` shared by reference across every `useToast()` call. This is
intentional and different from the chat store's pattern; don't "fix" it into a store without reason.

**`tsconfig.app.json` sets `noUncheckedIndexedAccess: true`.** Any array index access
(`arr[i]`) types as possibly `undefined` — use optional chaining or a bounds check, not a
non-null assertion, when indexing into arrays.

**Path alias:** `@/*` → `src/*` (defined in both `vite.config.ts` and `tsconfig.app.json`; keep
both in sync if it ever changes).
