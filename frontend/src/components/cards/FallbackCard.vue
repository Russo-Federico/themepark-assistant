<script setup lang="ts">
import type { FallbackCard } from '@/types'

defineProps<{
  card: FallbackCard
}>()
</script>

<template>
  <div class="card fallback-card">
    <div class="fallback-content">
      <div class="message">
        {{ card.message }}
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
  opacity: 0.95;
}

.fallback-content {
  padding: 16px 0;
}

.message {
  font-family: var(--font-body);
  font-size: 15.5px;
  font-weight: 400;
  line-height: 1.6;
  color: var(--color-text-primary);
  padding: 2px 0;
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
