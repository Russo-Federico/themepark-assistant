<script setup lang="ts">
import { computed } from 'vue'
import type { AttractionCard } from '@/types'

const props = defineProps<{
  card: AttractionCard
}>()

// Splits a value like "2,400 guests / hr" into a bold leading number and a
// trailing unit rendered smaller and inline.
const numberParts = computed(() => {
  return props.card.fields.map((field) => {
    const match = String(field.value).match(/^([\d.,]+)\s*(.*)$/)
    return match ? { number: match[1], unit: match[2] } : { number: String(field.value), unit: '' }
  })
})
</script>

<template>
  <div class="card attraction-card">
    <!-- Header -->
    <div class="card-header">
      <div class="icon-tile">🎢</div>
      <div class="header-text">
        <h3 class="title">{{ card.title }}</h3>
        <span class="subtitle">
          {{ card.area }}<template v-if="card.subtitle"> · {{ card.subtitle }}</template>
        </span>
      </div>
    </div>

    <div class="divider"></div>

    <!-- Body -->
    <div class="card-body">
      <div class="fields-grid">
        <template v-for="(field, index) in card.fields" :key="index">
          <span class="field-label">{{ field.label }}</span>

          <div v-if="field.type === 'dots'" class="dots-container">
            <span
              v-for="i in 5"
              :key="i"
              class="dot"
              :class="{ filled: i <= (field.value as number) }"
            ></span>
          </div>

          <span
            v-else-if="field.type === 'wait_badge'"
            class="wait-badge"
            :class="`badge-${field.level}`"
          >
            {{ field.value }}
          </span>

          <span v-else-if="field.type === 'number'" class="number-value">
            {{ numberParts[index].number
            }}<span v-if="numberParts[index].unit" class="number-unit">
              {{ numberParts[index].unit }}</span
            >
          </span>

          <span v-else class="field-value">{{ field.value }}</span>
        </template>
      </div>

      <div v-if="card.badges.length > 0" class="badges-row">
        <span v-for="badge in card.badges" :key="badge" class="pill-badge" :class="`pill-${badge}`">
          <template v-if="badge === 'accessible'">♿ Accessible</template>
          <template v-else-if="badge === 'express_pass'">⚡ Express Pass</template>
        </span>
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
  background: var(--color-card-bg);
  border: 1px solid var(--color-card-border);
  border-radius: var(--radius-card);
  max-width: 380px;
  align-self: flex-start;
  animation: card-in 0.3s ease-out both;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 18px 20px;
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
  background: var(--color-icon-attraction-bg);
  color: var(--color-icon-attraction-fg);
  border-radius: 9px;
  font-size: 16px;
}

.header-text {
  display: flex;
  flex-direction: column;
}

.title {
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: 15px;
  color: var(--color-text-primary);
  margin: 0;
}

.subtitle {
  font-family: var(--font-body);
  font-weight: 500;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.divider {
  border-top: 1px solid var(--color-border-thin);
  margin: 14px 0;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.fields-grid {
  display: grid;
  grid-template-columns: 130px 1fr;
  row-gap: 14px;
  column-gap: 12px;
  align-items: center;
}

.field-label {
  font-family: var(--font-body);
  font-size: 12.5px;
  color: var(--color-text-secondary);
}

.field-value {
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--color-text-primary);
  font-weight: 500;
}

.number-value {
  font-family: var(--font-heading);
  font-size: 20px;
  font-weight: 800;
  color: var(--color-text-primary);
}

.number-unit {
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-left: 4px;
}

.dots-container {
  display: flex;
  gap: 6px;
}

.dot {
  width: 11px;
  height: 11px;
  border-radius: 50%;
  border: 1px solid var(--color-border-marked);
  background-color: transparent;
}

.dot.filled {
  background-color: var(--color-accent);
  border-color: var(--color-accent);
}

.wait-badge {
  padding: 4px 10px;
  border-radius: var(--radius-badge);
  font-size: 12px;
  font-weight: 500;
  justify-self: start;
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

.badges-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
}

.pill-badge {
  padding: 3px 8px;
  border-radius: var(--radius-badge);
  font-size: 11px;
  font-weight: 500;
}

.pill-accessible {
  background-color: var(--color-badge-accessible-bg);
  color: var(--color-badge-accessible-text);
}

.pill-express_pass {
  background-color: var(--color-badge-express-bg);
  color: var(--color-badge-express-text);
}

.card-footer {
  padding-top: var(--space-md);
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
