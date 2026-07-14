<script setup lang="ts">
defineProps<{
  content: string
}>()
</script>

<template>
  <div class="user-bubble-wrapper">
    <div class="user-bubble">
      {{ content }}
    </div>
  </div>
</template>

<style scoped>
.user-bubble-wrapper {
  display: flex;
  justify-content: flex-end;
  animation: bubble-in 0.3s ease-out both;
}

.user-bubble {
  max-width: 72%;
  padding: 11px 15px;
  background-color: var(--color-accent);
  color: var(--color-accent-text);
  font-family: var(--font-body);
  font-size: 14.5px;
  font-weight: 600;
  line-height: 1.5;
  border-radius: 999px;
  box-shadow: 0 6px 18px rgba(201, 162, 74, 0.19);
  word-break: break-word;
  white-space: pre-wrap;
}

@keyframes bubble-in {
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
