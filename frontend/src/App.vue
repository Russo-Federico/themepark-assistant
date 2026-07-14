<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useChatStore } from '@/stores/chat'
import AppHeader from './components/AppHeader.vue'
import InputBar from './components/InputBar.vue'
import ToastNotification from './components/ToastNotification.vue'
import SettingsPanel from './components/SettingsPanel.vue'
import ChatFeed from './components/ChatFeed.vue'

const chatStore = useChatStore()
const { isSettingsOpen } = storeToRefs(chatStore)
</script>

<template>
  <AppHeader />
  <SettingsPanel v-if="isSettingsOpen" />
  <ChatFeed v-else />
  <InputBar v-if="!isSettingsOpen" />
  <ToastNotification />
</template>

<style scoped>
/* Layout is handled by main.css on #app */
</style>
