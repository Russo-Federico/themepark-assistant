<script setup lang="ts">
import { ref, computed } from 'vue'
import { useChatStore } from '@/stores/chat'
import { storeToRefs } from 'pinia'

const chatStore = useChatStore()
const { messages } = storeToRefs(chatStore)

const compactFeed = ref(false)
const showTimestamps = ref(false)
const liveOpsAlerts = ref(true)
const capacityWarnings = ref(true)

const mockHistory = [
  { id: 1, title: 'Adventure World redirects', preview: 'Where can we redirect guests from the crowded…', time: '2h ago' },
  { id: 2, title: 'Dragon Flight accessibility', preview: 'What are the accessibility requirements for…', time: 'Yesterday' },
  { id: 3, title: 'Express Pass capacity check', preview: 'How many Express Pass slots are left for…', time: 'Mon' },
]

const currentConversation = computed(() => {
  const firstUser = messages.value.find((m) => m.role === 'user')
  if (!firstUser?.content) return null
  return {
    title: firstUser.content.length > 40 ? firstUser.content.slice(0, 40) + '…' : firstUser.content,
    preview: `${messages.value.filter((m) => m.role !== 'user').length} responses`,
    time: 'Now',
    initial: firstUser.content[0].toUpperCase(),
  }
})

function getInitial(title: string) {
  return title[0].toUpperCase()
}

function handleClearHistory() {
  chatStore.clearConversation()
  chatStore.isSettingsOpen = false
}
</script>

<template>
  <div class="settings-panel">
    <!-- Appearance -->
    <p class="section-label" style="margin-top: 0">Appearance</p>

    <div class="settings-card">
      <div class="setting-row">
        <span class="row-label">Compact feed</span>
        <button
          class="toggle"
          :class="{ active: compactFeed }"
          :aria-checked="compactFeed"
          role="switch"
          @click="compactFeed = !compactFeed"
        >
          <span class="toggle-knob"></span>
        </button>
      </div>
      <div class="divider"></div>
      <div class="setting-row">
        <span class="row-label">Show timestamps</span>
        <button
          class="toggle"
          :class="{ active: showTimestamps }"
          :aria-checked="showTimestamps"
          role="switch"
          @click="showTimestamps = !showTimestamps"
        >
          <span class="toggle-knob"></span>
        </button>
      </div>
    </div>

    <!-- Notifications -->
    <p class="section-label">Notifications</p>

    <div class="settings-card">
      <div class="setting-row">
        <div class="row-label-group">
          <span class="row-label">Live ops alerts</span>
          <span class="row-sublabel">Notify on extreme wait times</span>
        </div>
        <button
          class="toggle"
          :class="{ active: liveOpsAlerts }"
          :aria-checked="liveOpsAlerts"
          role="switch"
          @click="liveOpsAlerts = !liveOpsAlerts"
        >
          <span class="toggle-knob"></span>
        </button>
      </div>
      <div class="divider"></div>
      <div class="setting-row">
        <div class="row-label-group">
          <span class="row-label">Capacity warnings</span>
          <span class="row-sublabel">Flag attractions above 80% capacity</span>
        </div>
        <button
          class="toggle"
          :class="{ active: capacityWarnings }"
          :aria-checked="capacityWarnings"
          role="switch"
          @click="capacityWarnings = !capacityWarnings"
        >
          <span class="toggle-knob"></span>
        </button>
      </div>
    </div>

    <!-- Conversation History -->
    <p class="section-label">Conversation History</p>

    <div class="settings-card">
      <!-- Current session (if any messages) -->
      <template v-if="currentConversation">
        <div class="history-row">
          <div class="history-icon">{{ currentConversation.initial }}</div>
          <div class="history-text">
            <span class="history-title">{{ currentConversation.title }}</span>
            <span class="history-preview">{{ currentConversation.preview }}</span>
          </div>
          <span class="history-time">{{ currentConversation.time }}</span>
        </div>
        <div class="divider"></div>
      </template>

      <div v-for="(item, idx) in mockHistory" :key="item.id">
        <div class="history-row">
          <div class="history-icon">{{ getInitial(item.title) }}</div>
          <div class="history-text">
            <span class="history-title">{{ item.title }}</span>
            <span class="history-preview">{{ item.preview }}</span>
          </div>
          <span class="history-time">{{ item.time }}</span>
        </div>
        <div v-if="idx < mockHistory.length - 1" class="divider"></div>
      </div>
    </div>

    <!-- Clear History -->
    <p class="section-label">Danger Zone</p>

    <button class="clear-btn" @click="handleClearHistory">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      Clear conversation history
    </button>
  </div>
</template>

<style scoped>
.settings-panel {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: calc(var(--header-height) + 28px) 32px 28px;
  max-width: 640px;
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

.section-label {
  flex-shrink: 0;
  margin-top: 14px;
  margin-bottom: 0;
  font-family: var(--font-body);
  font-size: 11.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-text-weak);
}

.settings-card {
  flex-shrink: 0;
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-border-thin);
  border-radius: 16px;
  overflow: hidden;
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  gap: 16px;
}

.row-label-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.row-label {
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
}

.row-sublabel {
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 400;
  color: var(--color-text-secondary);
}

.divider {
  height: 1px;
  background-color: var(--color-border-marked);
  margin: 0 16px;
}

/* Toggle */
.toggle {
  position: relative;
  width: 42px;
  height: 24px;
  border-radius: 999px;
  background-color: var(--color-surface-2);
  border: 1px solid var(--color-border-marked);
  flex-shrink: 0;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.toggle.active {
  background: var(--color-accent-gradient);
  border-color: transparent;
}

.toggle-knob {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background-color: #ffffff;
  transition: transform 0.2s ease;
  pointer-events: none;
}

.toggle.active .toggle-knob {
  transform: translateX(18px);
}

/* History rows */
.history-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
}

.history-icon {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 1px solid var(--color-border-thin);
  background-color: var(--color-surface-2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-family: var(--font-heading);
  font-size: 14px;
  font-weight: 700;
  color: var(--color-accent);
}

.history-text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.history-title {
  font-family: var(--font-body);
  font-size: 13.5px;
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-preview {
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 400;
  color: var(--color-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-time {
  font-family: var(--font-body);
  font-size: 11.5px;
  font-weight: 400;
  color: var(--color-text-weak);
  flex-shrink: 0;
}

/* Clear button */
.clear-btn {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 14px 16px;
  border-radius: 16px;
  background-color: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.35);
  color: #f87171;
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.clear-btn:hover {
  background-color: rgba(239, 68, 68, 0.2);
}
</style>
