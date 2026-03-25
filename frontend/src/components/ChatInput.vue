<template>
  <div class="input-area" v-if="currentSession">
    <div class="input-toolbar">
      <div class="model-selector">
        <select v-model="localModel" @change="$emit('update:model', localModel)">
          <option value="deepseek-reasoner">DeepSeek Reasoner</option>
          <option value="deepseek-chat">DeepSeek Chat</option>
        </select>
      </div>
    </div>
    <div class="input-box-wrapper">
      <div class="input-box">
        <textarea
          v-model="localMessage"
          placeholder="输入消息，按 Enter 发送，Shift+Enter 换行..."
          @keydown="handleKeydown"
          rows="1"
          ref="inputRef"
          :disabled="agentRunning"
        ></textarea>
        <button 
          class="btn-send" 
          @click="send"
          :disabled="!localMessage.trim() || agentRunning"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M15.854.146a.5.5 0 0 1 .11.54l-5.819 14.547a.75.75 0 0 1-1.329.124l-3.178-4.995L.643 7.184a.75.75 0 0 1 .124-1.33L15.314.037a.5.5 0 0 1 .54.11ZM6.636 10.07l2.761 4.338L14.13 2.576 6.636 10.07Zm6.787-8.201L1.591 6.602l4.339 2.76 7.494-7.493Z"/>
          </svg>
        </button>
      </div>
      <div class="input-hint">Enter 发送 · Shift+Enter 换行</div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  currentSession: Object,
  model: String,
  agentRunning: Boolean
})

const emit = defineEmits(['update:model', 'send'])

const localMessage = ref('')
const localModel = ref(props.model)
const inputRef = ref(null)

// 同步外部 model
watch(() => props.model, (newVal) => {
  localModel.value = newVal
})

function handleKeydown(e) {
  if (e.shiftKey) {
    // Shift+Enter 换行，不处理
    return
  }
  if (e.key === 'Enter') {
    e.preventDefault()
    send()
  }
}

function send() {
  const content = localMessage.value.trim()
  if (!content || props.agentRunning) return
  
  emit('send', content)
  localMessage.value = ''
  adjustHeight()
}

function adjustHeight() {
  nextTick(() => {
    const textarea = inputRef.value
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px'
    }
  })
}

// 监听输入调整高度
watch(localMessage, adjustHeight)
</script>

<style scoped>
.input-area {
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.input-toolbar {
  display: flex;
  align-items: center;
  padding: 8px 20px 0;
}

.model-selector select {
  padding: 4px 10px;
  font-size: 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  cursor: pointer;
  outline: none;
}

.model-selector select:hover {
  border-color: var(--border-color);
}

.input-box-wrapper {
  padding: 8px 20px 16px;
}

.input-box {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 4px;
}

.input-box:focus-within {
  border-color: var(--accent);
}

.input-box textarea {
  flex: 1;
  padding: 10px 12px;
  font-size: 14px;
  line-height: 1.5;
  background: transparent;
  border: none;
  color: var(--text-primary);
  resize: none;
  outline: none;
  font-family: inherit;
  min-height: 44px;
  max-height: 200px;
}

.input-box textarea::placeholder {
  color: var(--text-muted);
}

.input-box textarea:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-send {
  width: 36px;
  height: 36px;
  margin: 4px;
  border: none;
  background: var(--user-bubble);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  flex-shrink: 0;
}

.btn-send:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-send:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.input-hint {
  text-align: center;
  margin-top: 6px;
  font-size: 11px;
  color: var(--text-muted);
}
</style>
