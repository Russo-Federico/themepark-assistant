<script setup lang="ts">
import type { GuideCard } from '@/types'

defineProps<{
  card: GuideCard
}>()

const emit = defineEmits<{
  'select-example': [question: string]
}>()
</script>

<template>
  <div class="card guide-card">
    <!-- Body -->
    <div class="card-body">
      <p class="message">{{ card.message }}</p>

      <div v-if="card.example_questions.length > 0" class="chips-row">
        <button
          v-for="(question, index) in card.example_questions"
          :key="index"
          type="button"
          class="chip"
          @click="emit('select-example', question)"
        >
          {{ question }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  background-color: transparent;
  max-width: 100%;
  align-self: flex-start;
  animation: card-in 0.3s ease-out both;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border-left: 3px solid var(--color-accent-guide);
  padding-left: var(--space-md);
}

.card-body {
  padding: 14px 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.message {
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 400;
  line-height: 1.6;
  color: var(--color-text-primary);
  margin: 0;
}

.chips-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.chip {
  font-family: var(--font-body);
  font-size: 12.5px;
  font-weight: 500;
  color: var(--color-text-primary);
  background-color: var(--color-input-bg);
  border: 1px solid var(--color-input-border);
  border-radius: var(--radius-pill);
  padding: 7px 14px;
  cursor: pointer;
  transition:
    border-color 0.2s ease,
    background-color 0.2s ease;
}

.chip:hover {
  border-color: var(--color-accent-guide);
  background-color: var(--color-surface-2);
}

@keyframes card-in {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
