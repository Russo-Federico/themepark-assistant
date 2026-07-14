<script setup lang="ts">
import type { LiveOpsCard } from '@/types'

defineProps<{
  card: LiveOpsCard
}>()
</script>

<template>
  <div class="card liveops-card">
    <!-- Header -->
    <div class="card-header">
      <div class="header-text">
        <h3 class="title">{{ card.title }}</h3>
        <span class="subtitle">{{ card.area }}</span>
      </div>
    </div>

    <!-- Body -->
    <div class="card-body">
      <div class="rows-list">
        <div v-for="(row, index) in card.rows" :key="index" class="live-row">
          <span class="row-name">{{ row.name }}</span>
          <span class="wait-badge" :class="`badge-${row.level}`"> {{ row.wait_minutes }} min </span>
        </div>
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
  border-left: 3px solid var(--color-accent-liveops);
  padding-left: var(--space-md);
}

.card-header {
  padding: 14px 0;
}

.header-text {
  display: flex;
  flex-direction: column;
}

.title {
  font-family: var(--font-heading);
  font-weight: 500;
  font-size: 15px;
  color: var(--color-text-primary);
  margin: 0;
}

.subtitle {
  font-family: var(--font-body);
  font-weight: 400;
  font-size: 11px;
  color: var(--color-text-secondary);
}

.card-body {
  padding: 0 0 14px 0;
}

.rows-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.live-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-card-border);
}

.live-row:last-child {
  padding-bottom: 0;
  border-bottom: none;
}

.row-name {
  font-family: var(--font-body);
  font-weight: 500;
  font-size: 14px;
  color: var(--color-text-primary);
}

.wait-badge {
  padding: 4px 10px;
  border-radius: var(--radius-badge);
  font-size: 12px;
  font-weight: 500;
}

.badge-low {
  background-color: var(--color-wait-low-bg);
  color: var(--color-wait-low-text);
}

.badge-med {
  background-color: var(--color-wait-med-bg);
  color: var(--color-wait-med-text);
}

.badge-high {
  background-color: var(--color-wait-high-bg);
  color: var(--color-wait-high-text);
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
