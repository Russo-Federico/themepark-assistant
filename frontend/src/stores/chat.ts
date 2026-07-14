import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { postQuery, MalformedResponseError } from '@/api/assistant'
import type { ChatMessage, HistoryEntry, ResponseCard } from '@/types'

const KNOWN_CARD_TYPES = ['attraction', 'live_ops', 'accessibility', 'event', 'guide', 'fallback']

const NETWORK_ERROR_MESSAGE = 'Could not reach the assistant. Check your connection.'
const MALFORMED_RESPONSE_MESSAGE =
  "Something went wrong reading the assistant's response. Please try again."

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const isScrolled = ref(false)
  const isSettingsOpen = ref(false)
  const draftQuery = ref<string | null>(null)

  // Build history array from messages for API calls
  const history = computed<HistoryEntry[]>(() => {
    return messages.value.reduce<HistoryEntry[]>((acc, msg) => {
      if (msg.role === 'user' && msg.content) {
        acc.push({ role: 'user', content: msg.content })
      } else if (msg.role === 'assistant' && msg.cards) {
        acc.push({ role: 'assistant', content: JSON.stringify(msg.cards) })
      }
      return acc
    }, [])
  })

  function generateId(): string {
    return `msg-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
  }

  async function sendMessage(query: string) {
    if (!query.trim() || isLoading.value) return

    error.value = null

    // Add user message
    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: query.trim(),
    }
    messages.value.push(userMessage)

    // Set loading
    isLoading.value = true

    try {
      const response = await postQuery(query.trim(), history.value)

      // Defend against a response containing a card_type the frontend
      // doesn't know how to render (e.g. schema drift) — better to show one
      // clear fallback than have ChatFeed's switch silently skip a card.
      const hasUnknownCard = response.cards.some((card) => !KNOWN_CARD_TYPES.includes(card.card_type))
      const cards: ResponseCard[] = hasUnknownCard
        ? [{ card_type: 'fallback', message: MALFORMED_RESPONSE_MESSAGE } as ResponseCard]
        : response.cards

      const assistantMessage: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        cards,
        connector_label: hasUnknownCard ? null : response.connector_label,
      }
      messages.value.push(assistantMessage)
    } catch (err) {
      const message =
        err instanceof MalformedResponseError ? MALFORMED_RESPONSE_MESSAGE : NETWORK_ERROR_MESSAGE
      error.value = message

      const fallbackMessage: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        cards: [{ card_type: 'fallback', message } as ResponseCard],
      }
      messages.value.push(fallbackMessage)
    } finally {
      isLoading.value = false
    }
  }

  function clearConversation() {
    messages.value = []
    error.value = null
    isLoading.value = false
  }

  function setDraftQuery(query: string) {
    draftQuery.value = query
  }

  return {
    messages,
    isLoading,
    error,
    isScrolled,
    isSettingsOpen,
    draftQuery,
    history,
    sendMessage,
    clearConversation,
    setDraftQuery,
  }
})
