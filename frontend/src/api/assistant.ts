import type { ApiResponse, HistoryEntry } from '@/types'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

// Thrown when the backend responds (any status) but the body isn't usable —
// distinct from a fetch()-level failure, which means the backend is
// unreachable. The backend guarantees a valid FallbackCard body even on a
// 500, so a malformed body here means something is actually wrong upstream.
export class MalformedResponseError extends Error {}

export async function postQuery(query: string, history: HistoryEntry[]): Promise<ApiResponse> {
  const res = await fetch(`${API_BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, history }),
  })

  let data
  try {
    data = await res.json()
  } catch {
    throw new MalformedResponseError(`Response body was not valid JSON (status ${res.status})`)
  }

  if (!Array.isArray(data?.cards)) {
    throw new MalformedResponseError(`Response had no usable cards array (status ${res.status})`)
  }

  return {
    cards: data.cards,
    connector_label: data.connector_label ?? null,
    transcript: data.transcript ?? null,
  }
}
