// ── Card field types ──────────────────────────────────────────────

export interface CardField {
  label: string
  value: string | number
  type: 'text' | 'dots' | 'wait_badge' | 'number'
  level?: 'low' | 'med' | 'high'
}

export interface LiveOpsRow {
  name: string
  wait_minutes: number
  level: 'low' | 'med' | 'high'
}

export type BadgeType = 'accessible' | 'express_pass'

// ── Card types ────────────────────────────────────────────────────

export interface AttractionCard {
  card_type: 'attraction'
  title: string
  area: string
  subtitle?: string
  fields: CardField[]
  badges: BadgeType[]
  footer?: string
}

export interface LiveOpsCard {
  card_type: 'live_ops'
  title: string
  area: string
  rows: LiveOpsRow[]
}

export interface AccessibilityCard {
  card_type: 'accessibility'
  title: string
  area: string
  fields: CardField[]
  footer?: string
}

export interface EventCard {
  card_type: 'event'
  title: string
  area: string
  description: string
  footer?: string
}

export interface FallbackCard {
  card_type: 'fallback'
  message: string
}

export interface GuideCard {
  card_type: 'guide'
  message: string
  example_questions: string[]
}

export type ResponseCard =
  | AttractionCard
  | LiveOpsCard
  | AccessibilityCard
  | EventCard
  | FallbackCard
  | GuideCard

// ── API types ─────────────────────────────────────────────────────

export interface ApiResponse {
  cards: ResponseCard[]
  connector_label: string | null
  transcript: string | null
}

export interface HistoryEntry {
  role: 'user' | 'assistant'
  content: string
}

// ── Chat message types ────────────────────────────────────────────

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content?: string
  cards?: ResponseCard[]
  connector_label?: string | null
}
