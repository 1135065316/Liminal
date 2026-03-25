<template>
  <div class="chat-container" ref="chatContainer">
    <!-- 空状态 -->
    <div v-if="!currentSession" class="empty-state">
      <div class="empty-content">
        <div class="empty-icon">◐</div>
        <div class="empty-title">Liminal</div>
        <div class="empty-desc">选择一个会话开始对话，或创建新会话</div>
      </div>
    </div>
    
    <!-- 消息列表 -->
    <template v-else>
      <div class="messages-wrapper">
        <MessageItem
          v-for="(msg, index) in filteredMessages"
          :key="msg.id || index"
          :msg="msg"
          :is-expanded="expandedMessages.has(msg.id)"
          @toggle-expand="$emit('toggle-expand', $event)"
        />
      </div>
      
      <!-- 执行中状态栏 -->
      <div v-if="agentRunning" class="status-bar">
        <template v-if="isStopping">
          <span class="status-icon stopping">⏹</span>
          <span class="status-text stopping">正在停止...</span>
        </template>
        <template v-else>
          <span class="status-icon loading">◐</span>
          <span class="status-text">Agent 执行中</span>
          <div class="status-dots">
            <span></span><span></span><span></span>
          </div>
          <button class="btn-stop" @click="$emit('stop')">停止</button>
        </template>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref, watch, nextTick } from 'vue'
import MessageItem from './MessageItem.vue'

const props = defineProps({
  currentSession: Object,
  messages: Array,
  agentRunning: Boolean,
  isStopping: Boolean,
  expandedMessages: Set
})

const emit = defineEmits(['toggle-expand', 'stop', 'scroll'])

const chatContainer = ref(null)

// 过滤掉系统提示词消息（role 为 system 且不是执行结果的）
const filteredMessages = computed(() => {
  return props.messages.filter(msg => {
    // 如果是执行结果，显示
    if (msg.is_result) return true
    // 如果是 system 角色但不是执行结果，不显示（这是系统提示词）
    if (msg.role === 'system') return false
    // 其他都显示
    return true
  })
})

// 监听消息变化自动滚动
watch(() => props.messages.length, () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
})
</script>

<style scoped>
.chat-container {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-content {
  text-align: center;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.3;
}

.empty-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
}

.messages-wrapper {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px 20px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
}

.status-icon {
  font-size: 14px;
}

.status-icon.loading {
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.status-text {
  font-size: 13px;
  color: var(--text-secondary);
}

.status-text.stopping {
  color: var(--warning);
}

.status-dots {
  display: flex;
  gap: 4px;
}

.status-dots span {
  width: 4px;
  height: 4px;
  background: var(--text-muted);
  border-radius: 50%;
  animation: dotBounce 1.4s infinite ease-in-out both;
}

.status-dots span:nth-child(1) { animation-delay: -0.32s; }
.status-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.btn-stop {
  margin-left: 12px;
  padding: 4px 12px;
  font-size: 12px;
  color: var(--error);
  background: transparent;
  border: 1px solid var(--error);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-stop:hover {
  background: var(--error);
  color: white;
}
</style>
