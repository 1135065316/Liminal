<template>
  <div class="liminal-app">
    <!-- 侧边栏 -->
    <Sidebar
      :sessions="sessions"
      :current-session-id="currentSessionId"
      @create-session="showCreateDialog = true"
      @switch-session="switchSession"
      @rename-session="startRename"
      @delete-session="deleteSession"
    />

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 顶部栏 -->
      <TopBar
        :current-session="currentSession"
        :token-info="tokenInfo"
      />

      <!-- 对话区域 -->
      <ChatArea
        :current-session="currentSession"
        :messages="messages"
        :agent-running="agentRunning"
        :is-stopping="isStopping"
        :expanded-messages="expandedMessages"
        @toggle-expand="toggleExpand"
        @stop="stopAgent"
      />

      <!-- 聊天输入 -->
      <ChatInput
        :current-session="currentSession"
        v-model:model="selectedModel"
        :agent-running="agentRunning"
        @send="sendMessage"
      />
    </main>

    <!-- 创建会话弹窗 -->
    <CreateSessionDialog
      :show="showCreateDialog"
      @close="showCreateDialog = false"
      @create="createSession"
    />

    <!-- 重命名弹窗 -->
    <RenameDialog
      :show="showRenameDialog"
      v-model="renameValue"
      @close="showRenameDialog = false"
      @confirm="confirmRename"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import Sidebar from './components/Sidebar.vue'
import TopBar from './components/TopBar.vue'
import ChatArea from './components/ChatArea.vue'
import ChatInput from './components/ChatInput.vue'
import CreateSessionDialog from './components/CreateSessionDialog.vue'
import RenameDialog from './components/RenameDialog.vue'

const API_BASE = 'http://localhost:18080'

// 状态
const sessions = ref([])
const currentSessionId = ref(null)
const messages = ref([])
const agentRunning = ref(false)
const isStopping = ref(false)
const selectedModel = ref('deepseek-reasoner')
const tokenInfo = ref({ current: 0, limit: 128000, percentage: 0 })
const expandedMessages = ref(new Set())

// 弹窗状态
const showCreateDialog = ref(false)
const showRenameDialog = ref(false)
const renameSessionId = ref('')
const renameValue = ref('')

// 轮询定时器
let pollTimer = null

// 计算属性
const currentSession = computed(() => {
  return sessions.value.find(s => s.id === currentSessionId.value)
})

// 切换展开状态
function toggleExpand(msgId) {
  if (expandedMessages.value.has(msgId)) {
    expandedMessages.value.delete(msgId)
  } else {
    expandedMessages.value.add(msgId)
  }
}

// 获取会话列表
async function fetchSessions() {
  try {
    const res = await fetch(`${API_BASE}/api/sessions`)
    sessions.value = await res.json()
  } catch (err) {
    console.error('获取会话失败:', err)
  }
}

// 获取消息（轮询）
async function fetchMessages() {
  if (!currentSessionId.value) return
  
  try {
    const res = await fetch(`${API_BASE}/api/sessions/${currentSessionId.value}/messages`)
    const data = await res.json()
    
    messages.value = data.messages
    agentRunning.value = data.agent_running
    isStopping.value = data.is_stopping || false
  } catch (err) {
    console.error('获取消息失败:', err)
  }
}

// 开始轮询
function startPolling() {
  stopPolling()
  pollTimer = setInterval(() => {
    fetchMessages()
    fetchTokenInfo()
  }, 1000)
}

// 停止轮询
function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

// 创建会话
async function createSession(form) {
  try {
    const res = await fetch(`${API_BASE}/api/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })
    const session = await res.json()
    sessions.value.push(session)
    currentSessionId.value = session.id
    messages.value = []
    showCreateDialog.value = false
    startPolling()
  } catch (err) {
    console.error('创建会话失败:', err)
    alert('创建会话失败')
  }
}

// 切换会话
async function switchSession(session) {
  currentSessionId.value = session.id
  messages.value = []
  expandedMessages.value.clear()
  await fetchMessages()
  startPolling()
}

// 删除会话
async function deleteSession(id) {
  if (!confirm('确定删除此会话？')) return
  try {
    await fetch(`${API_BASE}/api/sessions/${id}`, { method: 'DELETE' })
    sessions.value = sessions.value.filter(s => s.id !== id)
    if (currentSessionId.value === id) {
      currentSessionId.value = null
      messages.value = []
      stopPolling()
    }
  } catch (err) {
    console.error('删除会话失败:', err)
  }
}

// 开始重命名
function startRename(session) {
  renameSessionId.value = session.id
  renameValue.value = session.name
  showRenameDialog.value = true
}

// 确认重命名
async function confirmRename(name) {
  try {
    await fetch(`${API_BASE}/api/sessions/${renameSessionId.value}/rename`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    })
    const session = sessions.value.find(s => s.id === renameSessionId.value)
    if (session) session.name = name
    showRenameDialog.value = false
  } catch (err) {
    console.error('重命名失败:', err)
  }
}

// 发送消息
async function sendMessage(content) {
  if (!currentSessionId.value || agentRunning.value) return
  
  try {
    const res = await fetch(`${API_BASE}/api/sessions/${currentSessionId.value}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, model: selectedModel.value })
    })
    const data = await res.json()
    
    if (data.success) {
      agentRunning.value = true
      await fetchMessages()
    } else {
      alert(data.error || '发送失败')
    }
  } catch (err) {
    console.error('发送消息失败:', err)
    alert('发送失败')
  }
}

// 停止 Agent
async function stopAgent() {
  if (!currentSessionId.value) return
  try {
    await fetch(`${API_BASE}/api/sessions/${currentSessionId.value}/stop`, {
      method: 'POST'
    })
    isStopping.value = true
  } catch (err) {
    console.error('停止失败:', err)
  }
}

// 获取 Token 信息
async function fetchTokenInfo() {
  try {
    const res = await fetch(`${API_BASE}/api/token-info`)
    tokenInfo.value = await res.json()
  } catch (err) {
    console.error('获取 Token 信息失败:', err)
  }
}

// 初始化
onMounted(() => {
  fetchSessions()
  fetchTokenInfo()
  setInterval(fetchTokenInfo, 10000)
})

// 清理
onUnmounted(() => {
  stopPolling()
})
</script>

<style>
/* ===== CSS 变量 ===== */
:root {
  --bg-primary: #0d1117;
  --bg-secondary: #161b22;
  --bg-tertiary: #21262d;
  --bg-hover: #1f2428;
  --bg-active: #2d333b;
  --border-color: #30363d;
  --border-light: #21262d;
  --text-primary: #c9d1d9;
  --text-secondary: #8b949e;
  --text-muted: #6e7681;
  --accent: #58a6ff;
  --accent-hover: #79c0ff;
  --success: #3fb950;
  --warning: #d29922;
  --error: #f85149;
  --user-bubble: #1f6feb;
  --font-mono: 'SF Mono', Monaco, Consolas, 'Courier New', monospace;
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: var(--font-sans);
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-primary);
  line-height: 1.5;
}

.liminal-app {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  min-width: 0;
}

/* ===== 滚动条 ===== */
::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
  background: #484f58;
}

::-webkit-scrollbar-corner {
  background: transparent;
}
</style>
