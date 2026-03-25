<template>
  <!-- 系统提示词消息：不显示（role 为 system 且不是执行结果） -->
  <div v-if="msg.role === 'system' && !msg.is_result" class="hidden"></div>
  
  <!-- 左侧消息：Assistant / System 结果 -->
  <div v-else-if="isLeftMessage" class="message-row left">
    <div class="message-avatar" :class="avatarClass">
      {{ avatar }}
    </div>
    <div class="message-bubble left">
      <div class="message-header">
        <span class="message-author">{{ author }}</span>
        <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
      </div>
      
      <!-- 思考过程（仅 assistant） -->
      <div v-if="msg.thought" class="thought-box">
        <div class="thought-label">💡 思考</div>
        <div class="thought-content">{{ msg.thought }}</div>
      </div>
      
      <!-- 命令（仅 assistant） -->
      <div v-if="showCommand" class="command-box">
        <div class="command-label">{{ isSkillCommand ? '⚡' : '$' }}</div>
        <code class="command-code">{{ msg.command }}</code>
      </div>
      
      <!-- 内容（执行结果或普通消息） -->
      <div v-if="showContent" class="message-body markdown-body" v-html="renderedContent"></div>
      
      <!-- 折叠控制 -->
      <div v-if="shouldCollapse" class="expand-hint">
        <button v-if="!isExpanded" class="btn-expand" @click="$emit('toggle-expand', msg.id)">
          展开 {{ lineCount - 5 }} 行
          <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 11L3 6h10l-5 5z"/>
          </svg>
        </button>
        <button v-else class="btn-expand" @click="$emit('toggle-expand', msg.id)">
          收起
          <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 5L3 10h10l-5-5z"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
  
  <!-- 右侧消息：User -->
  <div v-else class="message-row right">
    <div class="message-spacer"></div>
    <div class="message-bubble right">
      <div class="message-header">
        <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
        <span class="message-author">You</span>
      </div>
      <div class="message-body markdown-body" v-html="renderedContent"></div>
      <div v-if="shouldCollapse" class="expand-hint right">
        <button v-if="!isExpanded" class="btn-expand" @click="$emit('toggle-expand', msg.id)">
          展开 {{ lineCount - 5 }} 行
          <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 11L3 6h10l-5 5z"/>
          </svg>
        </button>
        <button v-else class="btn-expand" @click="$emit('toggle-expand', msg.id)">
          收起
          <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 5L3 10h10l-5-5z"/>
          </svg>
        </button>
      </div>
    </div>
    <div class="message-avatar user">👤</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  msg: Object,
  isExpanded: Boolean
})

defineEmits(['toggle-expand'])

// 判断是否在左侧显示（assistant 或执行结果）
const isLeftMessage = computed(() => {
  // is_result 为 true 表示执行结果，显示在左侧
  if (props.msg.is_result) return true
  // assistant 角色显示在左侧
  if (props.msg.role === 'assistant') return true
  // system 角色显示在左侧（如果不是系统提示词）
  if (props.msg.role === 'system' && props.msg.is_result) return true
  return false
})

// 头像
const avatar = computed(() => {
  if (props.msg.is_result) return '⚙'
  if (props.msg.role === 'assistant') return '🤖'
  return '💬'
})

const avatarClass = computed(() => {
  if (props.msg.is_result) return 'system'
  if (props.msg.role === 'assistant') return 'assistant'
  return 'default'
})

// 作者名称
const author = computed(() => {
  if (props.msg.is_result) return 'System'
  if (props.msg.role === 'assistant') return 'Assistant'
  if (props.msg.role === 'system') return 'System'
  return 'Unknown'
})

// 是否显示命令
const showCommand = computed(() => {
  return props.msg.command && 
         !props.msg.is_result && 
         !props.msg.command.startsWith('DONE:') && 
         !props.msg.command.startsWith('FAIL:')
})

// 是否是 Skill 命令
const isSkillCommand = computed(() => {
  const cmd = props.msg.command || ''
  // 匹配 skill 命令格式：函数名(参数)
  return /^[a-zA-Z_][a-zA-Z0-9_]*\s*\(/.test(cmd)
})

// 是否显示内容
const showContent = computed(() => {
  // 执行结果显示内容
  if (props.msg.is_result) return true
  // assistant 且没有 command（普通回复）显示内容
  if (props.msg.role === 'assistant' && !props.msg.command) return true
  return false
})

// 获取清理后的内容
function getCleanContent() {
  let content = props.msg.content || ''
  // 清理执行结果前缀
  if (content.startsWith('执行结果:\n```\n')) {
    content = content.replace('执行结果:\n```\n', '').replace('\n```\n\n请继续:', '')
  }
  return content.trim()
}

// 获取内容行数（基于清理后的内容）
const lineCount = computed(() => {
  const content = getCleanContent()
  if (!content) return 0
  // 如果内容为空或只有空白，返回0
  const lines = content.split('\n').filter(line => line.trim().length > 0)
  return lines.length
})

// 是否需要折叠
const shouldCollapse = computed(() => {
  // assistant 消息且有 command 的不折叠（JSON 不展示）
  if (props.msg.role === 'assistant' && props.msg.command) return false
  // 内容少于等于5行不折叠
  return lineCount.value > 5
})

// 渲染内容
const renderedContent = computed(() => {
  let content = getCleanContent()
  
  // 如果未展开且超过5行，截取前5行
  if (shouldCollapse.value && !props.isExpanded) {
    const lines = content.split('\n')
    content = lines.slice(0, 5).join('\n') + '\n...'
  }
  
  return marked.parse(content, { breaks: true })
})

// 格式化时间
function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const isToday = d.toDateString() === now.toDateString()
  
  if (isToday) {
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
  }
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}
</script>

<style scoped>
.hidden {
  display: none;
}

.message-row {
  display: flex;
  gap: 12px;
  max-width: 100%;
}

.message-row.right {
  justify-content: flex-end;
}

.message-spacer {
  flex: 1;
  min-width: 40px;
  max-width: 200px;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
}

.message-avatar.assistant,
.message-avatar.system {
  background: var(--bg-tertiary);
}

.message-avatar.user {
  background: var(--user-bubble);
  border-color: var(--user-bubble);
}

.message-bubble {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 12px;
  position: relative;
}

.message-bubble.left {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-bottom-left-radius: 4px;
}

.message-bubble.right {
  background: var(--user-bubble);
  color: white;
  border-bottom-right-radius: 4px;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 12px;
}

.message-bubble.left .message-header {
  color: var(--text-muted);
}

.message-bubble.right .message-header {
  color: rgba(255, 255, 255, 0.7);
  justify-content: flex-end;
}

.message-author {
  font-weight: 600;
}

.thought-box {
  margin-bottom: 10px;
  padding: 10px 12px;
  background: rgba(88, 166, 255, 0.1);
  border: 1px solid rgba(88, 166, 255, 0.2);
  border-radius: 8px;
}

.thought-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--accent);
  margin-bottom: 4px;
}

.thought-content {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.command-box {
  margin-bottom: 10px;
  padding: 10px 12px;
  background: rgba(63, 185, 80, 0.1);
  border: 1px solid rgba(63, 185, 80, 0.2);
  border-radius: 8px;
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.command-label {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--success);
  font-weight: 600;
  flex-shrink: 0;
}

.command-code {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--text-primary);
  word-break: break-all;
  line-height: 1.5;
}

:deep(.markdown-body) {
  font-size: 14px;
  line-height: 1.6;
}

.message-bubble.right :deep(.markdown-body) {
  color: white;
}

:deep(.markdown-body p) {
  margin: 0 0 8px;
}

:deep(.markdown-body p:last-child) {
  margin-bottom: 0;
}

:deep(.markdown-body pre) {
  margin: 8px 0;
  padding: 12px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  overflow-x: auto;
}

.message-bubble.right :deep(.markdown-body pre) {
  background: rgba(0, 0, 0, 0.2);
}

:deep(.markdown-body code) {
  font-family: var(--font-mono);
  font-size: 13px;
  background: rgba(0, 0, 0, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
}

:deep(.markdown-body pre code) {
  background: none;
  padding: 0;
}

:deep(.markdown-body ul),
:deep(.markdown-body ol) {
  margin: 8px 0;
  padding-left: 20px;
}

:deep(.markdown-body li) {
  margin: 4px 0;
}

:deep(.markdown-body blockquote) {
  margin: 8px 0;
  padding-left: 12px;
  border-left: 3px solid var(--border-color);
  color: var(--text-secondary);
}

.expand-hint {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
}

.message-bubble.right .expand-hint {
  border-top-color: rgba(255, 255, 255, 0.2);
}

.btn-expand {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  font-size: 12px;
  color: var(--accent);
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-expand:hover {
  background: var(--bg-hover);
  border-color: var(--accent);
}

.message-bubble.right .btn-expand {
  color: rgba(255, 255, 255, 0.8);
  border-color: rgba(255, 255, 255, 0.3);
}

.message-bubble.right .btn-expand:hover {
  background: rgba(255, 255, 255, 0.1);
}
</style>
