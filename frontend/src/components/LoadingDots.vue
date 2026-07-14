<script setup lang="ts"></script>

<template>
  <div class="loading-dots">
    <span class="dot"></span>
    <span class="dot"></span>
    <span class="dot"></span>
  </div>
</template>

<style scoped>
.loading-dots {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: var(--space-sm) var(--space-lg);
  animation: fade-in 0.3s ease-out both;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-accent);
  animation: dot-pulse 1.2s ease-in-out infinite;
}

.dot:nth-child(2) {
  animation-delay: 0.15s;
}

.dot:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes dot-pulse {
  0%,
  80%,
  100% {
    transform: scale(1);
    opacity: 0.5;
  }
  40% {
    transform: scale(1.4);
    opacity: 1;
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
