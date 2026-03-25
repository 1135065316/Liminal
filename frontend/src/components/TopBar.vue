<template>
  <header class="top-bar">
    <div class="top-bar-left">
      <div class="breadcrumb" v-if="currentSession">
        <span class="breadcrumb-item">{{ currentSession.name }}</span>
      </div>
      <div class="breadcrumb-placeholder" v-else>选择一个会话开始</div>
    </div>
    <div class="top-bar-right">
      <div class="token-badge" :class="{ warning: tokenInfo.percentage > 80 }">
        <span class="token-icon">◐</span>
        <span class="token-text">{{ tokenInfo.current }}/{{ tokenInfo.limit }}</span>
        <span class="token-percent">{{ tokenInfo.percentage }}%</span>
      </div>
    </div>
  </header>
</template>

<script setup>
defineProps({
  currentSession: Object,
  tokenInfo: Object
})
</script>

<style scoped>
.top-bar {
  height: 50px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.breadcrumb {
  display: flex;
  align-items: center;
}

.breadcrumb-item {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.breadcrumb-placeholder {
  font-size: 14px;
  color: var(--text-muted);
}

.token-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: var(--bg-tertiary);
  border-radius: 20px;
  font-size: 12px;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.token-badge.warning {
  border-color: var(--warning);
  color: var(--warning);
}

.token-icon {
  font-size: 10px;
}

.token-text {
  font-family: var(--font-mono);
}
</style>
