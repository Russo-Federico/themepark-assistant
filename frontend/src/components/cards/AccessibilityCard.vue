<script setup lang="ts">
import type { AccessibilityCard } from '@/types'

defineProps<{
  card: AccessibilityCard
}>()
</script>

<template>
  <div class="card accessibility-card">
    <!-- Header -->
    <div class="card-header">
      <div class="header-text">
        <h3 class="title">{{ card.title }}</h3>
        <span class="subtitle">{{ card.area }}</span>
      </div>
    </div>

    <!-- Body -->
    <div class="card-body">
      <div class="fields-list">
        <div v-for="(field, index) in card.fields" :key="index" class="field-row">
          <span class="field-label">{{ field.label }}</span>
          <span class="field-value">{{ field.value }}</span>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div v-if="card.footer" class="card-footer">
      {{ card.footer }}
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
  border-left: 3px solid var(--color-accent-accessibility);
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

.fields-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.field-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.field-label {
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--color-text-secondary);
}

.field-value {
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--color-text-primary);
  font-weight: 500;
}

.card-footer {
  padding: var(--space-md) 0;
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.5;
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
