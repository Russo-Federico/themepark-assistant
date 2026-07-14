<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useToast } from '@/composables/useToast'
import { storeToRefs } from 'pinia'

const chatStore = useChatStore()
const { isLoading, draftQuery } = storeToRefs(chatStore)
const { showToast } = useToast()

const inputText = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)

watch(draftQuery, (query) => {
  if (!query) return
  inputText.value = query
  draftQuery.value = null
  nextTick(() => {
    adjustTextareaHeight()
    textareaRef.value?.focus()
  })
})

function handleMicClick() {
  if (isLoading.value) return
  showToast('Voice input — coming soon.', 'info')
}

function adjustTextareaHeight() {
  if (!textareaRef.value) return
  textareaRef.value.style.height = 'auto'
  const newHeight = Math.min(textareaRef.value.scrollHeight, 88)
  textareaRef.value.style.height = `${newHeight}px`
}

watch(inputText, () => {
  nextTick(adjustTextareaHeight)
})

watch(isLoading, (loading) => {
  if (!loading) {
    nextTick(() => {
      textareaRef.value?.focus()
    })
  }
})

function submitMessage(e?: Event) {
  if (e) e.preventDefault()
  const text = inputText.value.trim()
  if (!text || isLoading.value) return
  chatStore.sendMessage(text)
  inputText.value = ''
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  })
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    submitMessage()
  }
}
</script>

<template>
  <div class="input-bar-container">
    <div class="input-pill">
      <!-- Mic Button -->
      <button
        class="mic-btn"
        :class="{ disabled: isLoading }"
        :disabled="isLoading"
        aria-label="Voice input"
        @click="handleMicClick"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="9" y="2" width="6" height="12" rx="3" stroke="currentColor" stroke-width="1.6" />
          <path
            d="M19 11a7 7 0 01-14 0"
            stroke="currentColor"
            stroke-width="1.6"
            stroke-linecap="round"
          />
          <line x1="12" y1="18" x2="12" y2="22" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
          <line x1="8" y1="22" x2="16" y2="22" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
        </svg>
      </button>

      <!-- Text Input -->
      <textarea
        ref="textareaRef"
        v-model="inputText"
        class="text-input"
        placeholder="Ask anything about the park…"
        rows="1"
        :disabled="isLoading"
        @keydown="handleKeydown"
        @input="adjustTextareaHeight"
      ></textarea>

      <!-- Send Button -->
      <button
        class="send-btn"
        :class="{ disabled: isLoading || !inputText.trim() }"
        :disabled="isLoading || !inputText.trim()"
        aria-label="Send message"
        @click="submitMessage"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path
            d="M12 19V5M12 5L5 12M12 5L19 12"
            stroke="white"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.input-bar-container {
  padding: 0 24px 24px;
  background-color: var(--color-bg);
  flex-shrink: 0;
  display: flex;
  justify-content: center;
}

.input-pill {
  display: flex;
  align-items: flex-end;
  width: 100%;
  max-width: 720px;
  background-color: var(--color-input-bg);
  border: 1px solid var(--color-input-border);
  border-radius: 999px;
  padding: 10px 10px 10px 18px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
}

.mic-btn {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: transparent;
  color: var(--color-text-secondary);
  transition: color 0.2s ease;
}

.mic-btn:hover:not(.disabled) {
  color: var(--color-text-primary);
}

.mic-btn.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.text-input {
  flex: 1;
  background-color: transparent;
  border: none;
  padding: 7px var(--space-md);
  color: var(--color-text-primary);
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 400;
  resize: none;
  overflow-y: auto;
  line-height: 1.5;
  max-height: 88px;
}

.text-input::placeholder {
  color: var(--color-input-placeholder);
}

.text-input:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.send-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: var(--color-accent-gradient);
  transition: opacity 0.2s ease;
}

.send-btn:hover:not(.disabled) {
  opacity: 0.88;
}

.send-btn.disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
</style>
