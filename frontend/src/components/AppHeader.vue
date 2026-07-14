<script setup lang="ts">
import { useChatStore } from '@/stores/chat'
import { storeToRefs } from 'pinia'

const chatStore = useChatStore()
const { isSettingsOpen } = storeToRefs(chatStore)

function toggleSettings() {
  isSettingsOpen.value = !isSettingsOpen.value
}
</script>

<template>
  <header class="app-header">
    <div class="header-left">
      <div class="logo-mark">
        <svg
          width="21"
          height="21"
          viewBox="0 0 256 256"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <g fill="#1b1608">
            <path
              d="M132.1,14.7c-63,0-114.2,51.2-114.2,114.2c0,29.8,11.4,56.9,30.2,77.2c-1.9,3.8-3,8-3,12.5
              c0,15.2,12.4,27.6,27.6,27.6c8.4,0,16-3.8,21.1-9.8c12,4.3,24.9,6.6,38.4,6.6c63,0,114.2-51.2,114.2-114.2
              C246.3,65.9,195.1,14.7,132.1,14.7z M132.1,232.9c-11.6,0-22.8-1.9-33.3-5.5c0.9-2.8,1.5-5.7,1.5-8.8
              c0-15.2-12.4-27.6-27.6-27.6c-7,0-13.4,2.6-18.3,6.9c-16.3-18.4-26.3-42.6-26.3-69c0-57.4,46.7-104,104-104
              s104,46.7,104,104S189.5,232.9,132.1,232.9z"
            />
            <path
              d="M132.1,72.6c-19.7,0-37.1,10.4-46.9,25.9c3.1,2.2,5.1,5.7,5.1,9.8c0,6.6-5.4,12-12,12
              c-0.4,0-0.7,0-1.1-0.1c-0.4,2.6-0.6,5.2-0.6,7.8c0,30.6,24.9,55.4,55.4,55.4c30.6,0,55.4-24.9,55.4-55.4
              C187.6,97.4,162.7,72.6,132.1,72.6z M132.1,151.5c-13,0-23.5-10.5-23.5-23.5c0-13,10.5-23.5,23.5-23.5
              c13,0,23.5,10.5,23.5,23.5C155.6,141,145.1,151.5,132.1,151.5z"
            />
            <path
              d="M132.1,49.2c-43.5,0-78.8,35.4-78.8,78.8s35.4,78.8,78.8,78.8s78.8-35.4,78.8-78.8
              S175.6,49.2,132.1,49.2z M132.1,188.8c-33.5,0-60.8-27.3-60.8-60.8c0-3.2,0.3-6.4,0.8-9.5c-3.4-2.1-5.7-5.9-5.7-10.2
              c0-6.6,5.4-12,12-12c0.6,0,1.2,0.1,1.8,0.2c10.7-17.5,30-29.3,52-29.3c33.5,0,60.8,27.3,60.8,60.8
              C193,161.5,165.7,188.8,132.1,188.8z"
            />
          </g>
        </svg>
      </div>

      <div class="header-titles">
        <span class="app-name">Epic Worlds</span>
        <span class="app-subtitle">Staff Assistant</span>
      </div>
    </div>

    <div class="header-right">
      <div class="live-status">
        <span class="live-dot"></span>
        <span class="live-label">Live</span>
      </div>

      <button
        class="settings-btn"
        :aria-label="isSettingsOpen ? 'Close settings' : 'Open settings'"
        @click="toggleSettings"
      >
        <!-- Gear icon when chat view -->
        <svg
          v-if="!isSettingsOpen"
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M12 15a3 3 0 100-6 3 3 0 000 6z"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
          <path
            d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 01-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33
            1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09a1.65 1.65 0 00-1.08-1.51 1.65 1.65 0 00-1.82.33l-.06.06
            a2 2 0 01-2.83-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09
            a1.65 1.65 0 001.51-1.08 1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06
            a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51
            1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9
            a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1.08z"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
        <!-- Close (X) icon when settings view -->
        <svg
          v-else
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M18 6L6 18M6 6l12 12"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </button>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--header-height);
  padding: 0 22px;
  background-color: var(--color-header-bg);
  border-bottom: 1px solid var(--color-border-thin);
  flex-shrink: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.logo-mark {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--color-accent);
  box-shadow: 0 4px 14px rgba(201, 162, 74, 0.27);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.header-titles {
  display: flex;
  align-items: baseline;
  gap: var(--space-sm);
}

.app-name {
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: 16px;
  color: #ffffff;
  letter-spacing: -0.01em;
}

.app-subtitle {
  font-family: var(--font-body);
  font-weight: 500;
  font-size: 12.5px;
  color: var(--color-text-secondary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
}

.live-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-live-dot);
  animation: live-pulse 2s ease-in-out infinite;
}

@keyframes live-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.35; }
}

.live-label {
  font-family: var(--font-body);
  font-weight: 600;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.settings-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-surface-1);
  border: 1px solid var(--color-border-thin);
  color: var(--color-text-secondary);
  flex-shrink: 0;
  transition: color 0.2s ease, background-color 0.2s ease;
}

.settings-btn:hover {
  color: var(--color-text-primary);
  background-color: var(--color-surface-2);
}
</style>
