<script setup lang="ts">
defineProps<{
  label: string
}>()
</script>

<template>
  <div class="connector-label">
    <div class="line"></div>
    <span class="text">{{ label }}</span>
  </div>
</template>

<style scoped>
.connector-label {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-top: var(--space-xs);
  margin-bottom: var(--space-xs);
  max-width: 88%;
}

.line {
  flex: 0 0 24px;
  height: 1px;
  background-color: var(--color-card-border);
}

.text {
  font-family: var(--font-body);
  font-style: italic;
  font-size: 13px;
  color: var(--color-text-secondary);
}
</style>
