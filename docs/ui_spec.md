# Epic Worlds Staff Assistant — UI Specification

> This document describes the visual design and interaction flow of the Epic Worlds Staff Assistant. It is intended as input for a vibe coding tool and should be treated as the single source of truth for all frontend decisions.

---

## Concept

A single-purpose internal tool for theme park employees. The interface should feel like it was designed by the park itself — branded, modern, and confident — not like a generic chatbot bolted onto a dashboard. Think of it as the difference between a park's official mobile app and a generic helpdesk tool. Every visual decision reinforces that this is an Epic Worlds product.

The UI must be equally comfortable in two contexts: at a desk in a back-office setting, and on a mobile device on a busy park floor. This means large touch targets, high contrast, and responses that are scannable at a glance.

---

## Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| Brand Blue (primary) | `#1B2A6B` | Header background, buttons, user message bubbles |
| Teal (accent) | `#00D4C8` | Logo mark background, mic icon color, thrill dots, status dot |
| Background | `#F8F7F4` | App background, input bar background |
| Input Field | `#E8ECF5` | Text input background — blue-tinted, clearly part of the brand |
| Input Border | `#B5C0DC` | Text input border |
| Input Placeholder | `#6B7AAB` | Muted blue-grey, readable but clearly placeholder |
| Text Primary | `#1A1A2E` | All main body text |
| Text Secondary | `#6B7AAB` | Labels, subtitles, card metadata |
| Card Background | `#FFFFFF` | All response cards |
| Card Border | `#E5E7EB` | Subtle card and divider borders |

### Card Accent Colors (left border system)

Each card type carries a 3px left border as a visual category signal — employees learn at a glance what kind of response they're reading.

| Card Type | Left Border | Icon Background | Icon Color |
|-----------|-------------|-----------------|------------|
| Attraction info | none (clean white) | `#E1F5EE` | `#0F6E56` |
| Live ops / wait times | `#EF9F27` (amber) | `#FAEEDA` | `#854F0B` |
| Accessibility | `#00D4C8` (teal) | `#E1F5EE` | `#0F6E56` |
| Events | `#8B5CF6` (purple) | `#EDE9FE` | `#5B21B6` |

### Status and Badge Colors

| State | Background | Text |
|-------|------------|------|
| Wait: high (60+ min) | `#FCEBEB` | `#A32D2D` |
| Wait: medium (20–59 min) | `#FAEEDA` | `#854F0B` |
| Wait: low (under 20 min) | `#E1F5EE` | `#0F6E56` |
| Badge: Accessible | `#E1F5EE` | `#0F6E56` |
| Badge: Express Pass | `#E6F1FB` | `#185FA5` |

---

## Typography

| Role | Font | Weight | Size |
|------|------|--------|------|
| App name, card titles, area headings | Outfit (Google Fonts) | 500–600 | 15px / 16px |
| Body text, labels, input | Inter (Google Fonts) | 400–500 | 13px–14px |
| Badges, timestamps, metadata | Inter | 400 | 11px–12px |

Minimum body text size: **13px**. Never go below this — the app must be readable at arm's length outdoors.

---

## Layout Structure

The app is a single-screen layout with three vertical zones. There is no navigation, no sidebar, no tabs. This is a single-purpose tool and the UI reflects that.

```
┌─────────────────────────────────┐
│           HEADER                │  fixed, never scrolls
├─────────────────────────────────┤
│                                 │
│           FEED                  │  scrollable, cards stack top to bottom
│                                 │  most recent at the bottom
│                                 │
├─────────────────────────────────┤
│           INPUT BAR             │  fixed, always visible
└─────────────────────────────────┘
```

---

## Header

- **Background:** Brand Blue `#1B2A6B`
- **Height:** ~56px
- **Left side:** Logo mark (teal rounded square with a planet icon) + app name "Epic Worlds" in white Outfit semibold + "Staff Assistant" in muted white smaller text beside it
- **Right side:** Live status indicator (small teal dot + "Live" label in muted white) + settings gear icon in muted white
- The header never changes. It is purely informational.

---

## Feed (Message Area)

- **Background:** `#F8F7F4`
- **Padding:** 24px top, 20px horizontal, 12px bottom
- **Gap between items:** 16px
- Messages and cards stack vertically, newest at the bottom
- Previous responses are dimmed to **45% opacity** to give visual focus to the latest response without losing history
- No timestamps, no avatars, no "typing" indicators — clean and minimal

### User Message Bubbles

- **Background:** Brand Blue `#1B2A6B`
- **Text:** White, 14px Inter
- **Border radius:** 18px 18px 4px 18px (standard chat bubble, sharp bottom-right corner)
- **Alignment:** Right-aligned
- **Max width:** 75% of the feed width

### Response Cards

Cards are the primary output format. They are white, rounded, and bordered. They never contain long paragraphs — they are structured, scannable, and action-oriented.

**Card anatomy (top to bottom):**

1. **Card header** — icon + title + subtitle, separated from body by a hairline border
2. **Card body** — rows of label / value pairs, thrill dots, badges
3. **Card divider** — hairline border
4. **Card footer** — one or two lines of plain-language context or reasoning (e.g. "High capacity makes it an effective load-balancer for Adventure World peaks")

**Card header details:**
- Icon: 32×32px rounded square (8px radius), colored background per category
- Title: Outfit 500, 15px, text primary
- Subtitle: Inter 400, 11px, text secondary — shows area + context (e.g. "Fable World · similar thrill profile")

**Card body details:**
- Each row: label on the left (with small icon), value on the right
- Thrill level: rendered as 5 dots, filled in teal for active levels
- Wait times: rendered as colored badges (high/med/low system above)
- Feature badges (Accessible, Express Pass): small pill badges, left-aligned as a row

**Card max width:** 88% of the feed width (left-aligned, cards come from the assistant side)

---

## Input Bar

- **Background:** `#F8F7F4` (same as feed — no visual break, seamless)
- **Top border:** 0.5px hairline in card border color
- **Padding:** 12px top, 16px horizontal, 16px bottom
- **Layout (left to right):** Mic button — Text input — Send button

### Mic Button (left)
- **Shape:** Circle, 40×40px
- **Background:** Brand Blue `#1B2A6B`
- **Icon:** Microphone, teal `#00D4C8`, 18px
- The teal icon on the blue background creates a strong visual signal — this is a primary action
- When recording: the button pulses with a subtle teal glow animation

### Text Input (center)
- **Background:** `#E8ECF5` — clearly blue-tinted, belongs to the brand
- **Border:** 0.5px `#B5C0DC`
- **Border radius:** 24px (pill shape)
- **Placeholder text:** "Ask anything about the park…" in `#6B7AAB`
- **Text color:** `#1A1A2E`
- Expands vertically for multi-line input (max 4 lines before scrolling)

### Send Button (right)
- **Shape:** Circle, 40×40px
- **Background:** Brand Blue `#1B2A6B`
- **Icon:** Arrow up, white, 17px
- Same size as mic button — the two buttons are visually equal in weight

---

## Interaction Flow

### Standard text query

1. Employee types a question in the input field
2. Taps the send button (arrow up)
3. The user message appears as a blue bubble, right-aligned, at the bottom of the feed
4. A subtle loading state appears below the bubble (three teal dots pulsing)
5. The loading state is replaced by a response card, left-aligned
6. Previous items in the feed dim to 45% opacity
7. The feed scrolls to keep the latest card fully visible
8. The input field clears and returns focus

### Voice query

1. Employee taps the mic button (left of input)
2. The mic button background pulses with a soft teal glow — recording is active
3. Employee speaks their question
4. Employee taps mic again to stop (or silence detection triggers automatically)
5. The spoken query appears as a blue bubble (transcribed text) — same as text query from this point
6. Flow continues as standard text query above

### Image query

1. Employee taps a camera/attachment icon (small, inside or beside the input field)
2. Device camera or photo library opens
3. Employee selects or captures an image
4. A thumbnail preview appears in the input area above the text field
5. Employee optionally adds a text question alongside the image
6. Taps send — the image thumbnail + text appear as a combined user bubble
7. Response card appears as normal

### Orchestrated multi-step response (Live Ops + RAG)

This is the key scenario — a two-step response where the system fetches live data first, then uses it to query the knowledge base.

1. Employee asks a compound question (e.g. "Where can we redirect guests from the most crowded rides?")
2. User bubble appears as normal
3. Loading state appears
4. A **Live Ops card** appears first (amber left border) — showing current wait times for the crowded attractions, retrieved from the live ops agent
5. A brief connector line or label between the two cards reads "Based on live data, suggested redirects:" — visually linking the two responses
6. One or more **Attraction cards** appear below (white, no left border) — the RAG agent's redirect suggestions, with thrill level, capacity, and current wait
7. The card footer on each attraction card explains *why* it was suggested (the orchestrator's reasoning made visible)

---

## What the App Does NOT Have

- No sidebar or navigation drawer
- No persistent conversation history panel (current session only)
- No user profile or login screen (assumed authenticated via internal SSO)
- No dark mode (brand palette is light-first)
- No animations beyond the mic pulse and subtle card fade-in
- No markdown rendering in responses — everything is structured card UI, never raw text blocks
