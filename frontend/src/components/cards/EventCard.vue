<script setup lang="ts">
import type { EventCard } from '@/types'

defineProps<{
  card: EventCard
}>()
</script>

<template>
  <div class="card event-card">
    <div class="card-body">
      <span class="eyebrow-badge">Special event</span>

      <div class="card-header">
        <div class="icon-tile">🎉</div>
        <div class="header-text">
          <h3 class="title">{{ card.title }}</h3>
          <span class="area"> · {{ card.area }}</span>
        </div>
      </div>

      <p class="description">{{ card.description }}</p>
    </div>

    <!-- Footer meta bar -->
    <div v-if="card.footer" class="card-footer">
      <span class="footer-icon">🎟️</span>
      <span class="footer-text">{{ card.footer }}</span>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: var(--color-card-bg);
  border: 1px solid var(--color-card-border);
  border-radius: var(--radius-card);
  max-width: 380px;
  align-self: flex-start;
  animation: card-in 0.3s ease-out both;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.card-body {
  padding: 18px 20px 14px;
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.eyebrow-badge {
  align-self: flex-start;
  font-family: var(--font-body);
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--color-icon-event-fg);
  background: var(--color-icon-event-bg);
  border-radius: var(--radius-pill);
  padding: 4px 10px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.icon-tile {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-icon-event-bg);
  color: var(--color-icon-event-fg);
  border-radius: 9px;
  font-size: 16px;
}

.header-text {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
}

.title {
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: 15px;
  color: var(--color-text-primary);
  margin: 0;
}

.area {
  font-family: var(--font-body);
  font-weight: 500;
  font-size: 12.5px;
  color: var(--color-text-secondary);
}

.description {
  font-family: var(--font-body);
  font-size: 13.5px;
  line-height: 1.55;
  color: var(--color-text-primary);
  margin: 0;
}

.card-footer {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  border-top: 1px solid var(--color-border-thin);
  background: var(--color-surface-2);
  padding: 12px 20px;
  font-family: var(--font-body);
  font-size: 12.5px;
  font-weight: 700;
  color: var(--color-text-primary);
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
