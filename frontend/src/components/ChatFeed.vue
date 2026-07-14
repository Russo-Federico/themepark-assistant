<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useChatStore } from '@/stores/chat'
import type {
  ResponseCard,
  AttractionCard as AttractionCardType,
  LiveOpsCard as LiveOpsCardType,
  AccessibilityCard as AccessibilityCardType,
  EventCard as EventCardType,
  FallbackCard as FallbackCardType,
  GuideCard as GuideCardType,
} from '@/types'

import UserBubble from './UserBubble.vue'
import LoadingDots from './LoadingDots.vue'
import ConnectorLabel from './ConnectorLabel.vue'
import AttractionCard from './cards/AttractionCard.vue'
import LiveOpsCard from './cards/LiveOpsCard.vue'
import AccessibilityCard from './cards/AccessibilityCard.vue'
import EventCard from './cards/EventCard.vue'
import FallbackCard from './cards/FallbackCard.vue'
import GuideCard from './cards/GuideCard.vue'

const chatStore = useChatStore()
const { messages, isLoading } = storeToRefs(chatStore)

const feedRef = ref<HTMLElement | null>(null)

// Auto-scroll to bottom
function scrollToBottom() {
  if (!feedRef.value) return

  feedRef.value.scrollTo({
    top: feedRef.value.scrollHeight,
    behavior: 'smooth',
  })
}

// Watch for new messages or loading state changes to scroll
watch(
  () => messages.value.length,
  () => {
    nextTick(scrollToBottom)
  },
)

watch(isLoading, (loading) => {
  if (loading) {
    nextTick(scrollToBottom)
  }
})

// Scroll handler for Zero-UI header
function onScroll() {
  if (!feedRef.value) return
  chatStore.isScrolled = feedRef.value.scrollTop > 10
}

// Index (0-based) at which to render the connector label between a leading
// run of live_ops cards and the cards that follow (e.g. redirect suggestions).
// Returns -1 when there's no such split, so the label falls back to sitting
// above all cards.
function connectorSplitIndex(cards: ResponseCard[]): number {
  let i = 0
  while (i < cards.length && cards[i]?.card_type === 'live_ops') i++
  return i > 0 && i < cards.length ? i : -1
}
</script>

<template>
  <div class="chat-feed" ref="feedRef" @scroll="onScroll">
    <div class="feed-content">
      <template v-for="msg in messages" :key="msg.id">
        <div class="message-group">
          <!-- User message -->
          <UserBubble v-if="msg.role === 'user'" :content="msg.content!" />

          <!-- Assistant response -->
          <template v-else>
            <!-- Connector label if present, unless it belongs between two card groups below -->
            <ConnectorLabel
              v-if="msg.connector_label && connectorSplitIndex(msg.cards ?? []) === -1"
              :label="msg.connector_label"
            />

            <!-- Cards -->
            <template v-if="msg.cards">
              <template v-for="(card, ci) in msg.cards" :key="ci">
                <AttractionCard
                  v-if="card.card_type === 'attraction'"
                  :card="card as AttractionCardType"
                />
                <LiveOpsCard
                  v-else-if="card.card_type === 'live_ops'"
                  :card="card as LiveOpsCardType"
                />
                <AccessibilityCard
                  v-else-if="card.card_type === 'accessibility'"
                  :card="card as AccessibilityCardType"
                />
                <EventCard v-else-if="card.card_type === 'event'" :card="card as EventCardType" />
                <GuideCard
                  v-else-if="card.card_type === 'guide'"
                  :card="card as GuideCardType"
                  @select-example="chatStore.setDraftQuery($event)"
                />
                <FallbackCard
                  v-else-if="card.card_type === 'fallback'"
                  :card="card as FallbackCardType"
                />

                <!-- Connector label between the live-ops group and what follows -->
                <ConnectorLabel
                  v-if="msg.connector_label && connectorSplitIndex(msg.cards) === ci + 1"
                  :label="msg.connector_label"
                />
              </template>
            </template>
          </template>
        </div>
      </template>

      <!-- Loading dots -->
      <LoadingDots v-if="isLoading" />
    </div>
  </div>
</template>

<style scoped>
.chat-feed {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: var(--feed-padding-top) var(--feed-padding-x) var(--feed-padding-bottom);
}

.feed-content {
  display: flex;
  flex-direction: column;
  gap: var(--feed-gap);
  min-height: 100%;
  justify-content: flex-end; /* Pushes content to bottom when feed is not full */
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
}

.message-group {
  display: flex;
  flex-direction: column;
  gap: var(--feed-gap);
}
</style>
