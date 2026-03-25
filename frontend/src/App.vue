<template>
  <div class="liminal-app">
    <!-- 左侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <span class="logo-text">Liminal v1.0.0</span>
        <button class="btn-icon" @click="showCreateDialog = true" title="新建会话">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 2a.5.5 0 0 1 .5.5v5h5a.5.5 0 0 1 0 1h-5v5a.5.5 0 0 1-1 0v-5h-5a.5.5 0 0 1 0-1h5v-5A.5.5 0 0 1 8 2Z"/>
          </svg>
        </button>
      </div>
      
      <div class="session-list">
        <div
          v-for="session in sessions"
          :key="session.id"
          :class="['session-item', { active: currentSession?.id === session.id }]"
          @click="switchSession(session)"
        >
          <div class="session-info">
            <div class="session-name">{{ session.name }}</div>
            <div class="session-path" :title="session.project_path">{{ session.project_path }}</div>
          </div>
          <div class="session-actions">
            <button class="btn-icon-small" @click.stop="startRename(session)" title="重命名">
              <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
                <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"/>
              </svg>
            </button>
            <button class="btn-icon-small" @click.stop="deleteSession(session.id)" title="删除">
              <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
                <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 顶部栏 -->
      <header class="top-bar">
        <div class="session-title">{{ currentSession?.name || '请选择会话' }}</div>
        <div class="token-info" v-if="tokenInfo.limit > 0">
          <span class="token-text">{{ tokenInfo.current }}/{{ tokenInfo.limit }}</span>
          <span class="token-percentage" :class="{ warning: tokenInfo.percentage > 80 }">
            {{ tokenInfo.percentage }}%
          </span>
        </div>
      </header>

      <!-- 消息区域 -->
      <div class="chat-container" ref="chatContainer">
        <div v-if="!currentSession" class="empty-state">
          <div class="empty-icon">💬</div>
          <div class="empty-text">选择一个会话开始对话</div>
          <div class="empty-subtext">或点击左上角 + 创建新会话</div>
        </div>
        
        <template v-else>
          <div
            v-for="msg in currentSession.messages"
            :key="msg.id"
            :class="['message', msg.role]"
          >
            <div class="message-avatar">
              {{ msg.role === 'user' ? '👤' : '🤖' }}
            </div>
            <div class="message-content">
              <div class="message-header">
                <span class="message-role">{{ msg.role === 'user' ? 'User' : 'Assistant' }}</span>
                <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
              </div>
              <div class="message-body">{{ msg.content }}</div>
            </div>
          </div>
        </template>
      </div>

      <!-- 输入区域 -->
      <div class="input-area" v-if="currentSession">
        <div class="input-toolbar">
          <select v-model="selectedModel" class="model-select">
            <option value="deepseek-reasoner">DeepSeek Reasoner</option>
            <option value="deepseek-chat">DeepSeek Chat</option>
          </select>
        </div>
        <div class="input-box">
          <textarea
            v-model="inputMessage"
            placeholder="输入消息，按 Enter 发送..."
            @keydown.enter.prevent="sendMessage"
            rows="3"
          ></textarea>
          <button 
            class="btn-send" 
            @click="sendMessage"
            :disabled="!inputMessage.trim() || sending"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M15.854.146a.5.5 0 0 1 .11.54l-5.819 14.547a.75.75 0 0 1-1.329.124l-3.178-4.995L.643 7.184a.75.75 0 0 1 .124-1.33L15.314.037a.5.5 0 0 1 .54.11ZM6.636 10.07l2.761 4.338L14.13 2.576 6.636 10.07Zm6.787-8.201L1.591 6.602l4.339 2.76 7.494-7.493Z"/>
            </svg>
          </button>
        </div>
      </div>
    </main>

    <!-- 创建会话弹窗 -->
    <div v-if="showCreateDialog" class="modal-overlay" @click="showCreateDialog = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>创建新会话</h3>
          <button class="btn-close" @click="showCreateDialog = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>会话名称</label>
            <input v-model="newSession.name" placeholder="可选，默认自动生成" />
          </div>
          <div class="form-group">
            <label>项目路径 <span class="required">*</span></label>
            <input v-model="newSession.project_path" placeholder="如: C:\\Users\\name\\project" />
          </div>
          <div class="form-group">
            <label>会话类型</label>
            <select v-model="newSession.session_type">
              <option value="single">单 Agent</option>
              <option value="hierarchical" disabled>自上而下 Agent 集群 (预留)</option>
              <option value="emergent" disabled>涌现式 Agent 集群 (预留)</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showCreateDialog = false">取消</button>
          <button class="btn-primary" @click="createSession" :disabled="!newSession.project_path">
            创建
          </button>
        </div>
      </div>
    </div>

    <!-- 重命名弹窗 -->
    <div v-if="showRenameDialog" class="modal-overlay" @click="showRenameDialog = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>重命名会话</h3>
          <button class="btn-close" @click="showRenameDialog = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>新名称</label>
            <input v-model="renameValue" @keyup.enter="confirmRename" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showRenameDialog = false">取消</button>
          <button class="btn-primary" @click="confirmRename">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'

// API 基础地址
const API_BASE = 'http://localhost:18080'

// 状态
const sessions = ref([])
const currentSession = ref(null)
const inputMessage = ref('')
const selectedModel = ref('deepseek-reasoner')
const sending = ref(false)
const tokenInfo = ref({ current: 0, limit: 128000, percentage: 0 })
const chatContainer = ref(null)

// 弹窗状态
const showCreateDialog = ref(false)
const showRenameDialog = ref(false)
const newSession = ref({ name: '', project_path: '', session_type: 'single' })
const renameSessionId = ref('')
const renameValue = ref('')

// 获取会话列表
async function fetchSessions() {
  try {
    const res = await fetch(`${API_BASE}/api/sessions`)
    sessions.value = await res.json()
  } catch (err) {
    console.error('获取会话失败:', err)
  }
}

// 创建会话
async function createSession() {
  try {
    const res = await fetch(`${API_BASE}/api/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newSession.value)
    })
    const session = await res.json()
    sessions.value.push(session)
    currentSession.value = session
    showCreateDialog.value = false
    newSession.value = { name: '', project_path: '', session_type: 'single' }
  } catch (err) {
    console.error('创建会话失败:', err)
    alert('创建会话失败')
  }
}

// 切换会话
async function switchSession(session) {
  try {
    const res = await fetch(`${API_BASE}/api/sessions/${session.id}`)
    currentSession.value = await res.json()
    await nextTick()
    scrollToBottom()
  } catch (err) {
    console.error('切换会话失败:', err)
  }
}

// 删除会话
async function deleteSession(id) {
  if (!confirm('确定删除此会话？')) return
  try {
    await fetch(`${API_BASE}/api/sessions/${id}`, { method: 'DELETE' })
    sessions.value = sessions.value.filter(s => s.id !== id)
    if (currentSession.value?.id === id) {
      currentSession.value = null
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
async function confirmRename() {
  try {
    await fetch(`${API_BASE}/api/sessions/${renameSessionId.value}/rename`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: renameValue.value })
    })
    const session = sessions.value.find(s => s.id === renameSessionId.value)
    if (session) session.name = renameValue.value
    if (currentSession.value?.id === renameSessionId.value) {
      currentSession.value.name = renameValue.value
    }
    showRenameDialog.value = false
  } catch (err) {
    console.error('重命名失败:', err)
  }
}

// 发送消息
async function sendMessage() {
  const content = inputMessage.value.trim()
  if (!content || !currentSession.value || sending.value) return
  
  sending.value = true
  const tempContent = content
  inputMessage.value = ''
  
  // 乐观更新 - 先显示用户消息
  const userMsg = {
    id: Date.now().toString(),
    role: 'user',
    content: tempContent,
    timestamp: new Date().toISOString()
  }
  currentSession.value.messages.push(userMsg)
  scrollToBottom()
  
  try {
    const res = await fetch(`${API_BASE}/api/sessions/${currentSession.value.id}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: tempContent, model: selectedModel.value })
    })
    const data = await res.json()
    if (data.success) {
      currentSession.value.messages.push(data.message)
      scrollToBottom()
    }
  } catch (err) {
    console.error('发送消息失败:', err)
    alert('发送失败')
  } finally {
    sending.value = false
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

// 滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

// 格式化时间
function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

// 初始化
onMounted(() => {
  fetchSessions()
  fetchTokenInfo()
  // 定期刷新 token 信息
  setInterval(fetchTokenInfo, 5000)
})

// 监听消息变化自动滚动
watch(() => currentSession.value?.messages?.length, scrollToBottom)
</script>

<style>
/* CSS 变量 - VSCode 深色主题 */
:root {
  --bg-primary: #1e1e1e;
  --bg-secondary: #252526;
  --bg-tertiary: #2d2d30;
  --bg-hover: #2a2d2e;
  --bg-active: #37373d;
  --border-color: #3e3e42;
  --text-primary: #cccccc;
  --text-secondary: #9cdcfe;
  --text-muted: #858585;
  --accent: #007acc;
  --accent-hover: #0098ff;
  --success: #4ec9b0;
  --warning: #ce9178;
  --error: #f44336;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  font-size: 13px;
  color: var(--text-primary);
  background: var(--bg-primary);
}

.liminal-app {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* 侧边栏 */
.sidebar {
  width: 260px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  height: 40px;
  padding: 0 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-color);
}

.logo-text {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
}

.btn-icon {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: var(--text-primary);
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background: var(--bg-hover);
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.session-item {
  display: flex;
  align-items: center;
  padding: 8px 10px;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 2px;
  transition: background 0.15s;
}

.session-item:hover {
  background: var(--bg-hover);
}

.session-item:hover .session-actions {
  opacity: 1;
}

.session-item.active {
  background: var(--bg-active);
}

.session-info {
  flex: 1;
  min-width: 0;
}

.session-name {
  font-size: 13px;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-path {
  font-size: 11px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 2px;
}

.session-actions {
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.15s;
}

.btn-icon-small {
  width: 20px;
  height: 20px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon-small:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.top-bar {
  height: 40px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.session-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.token-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
}

.token-text {
  font-family: 'Consolas', monospace;
}

.token-percentage {
  padding: 2px 6px;
  border-radius: 3px;
  background: var(--bg-tertiary);
}

.token-percentage.warning {
  color: var(--warning);
  background: rgba(206, 145, 120, 0.2);
}

/* 聊天区域 */
.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-text {
  font-size: 16px;
  margin-bottom: 8px;
}

.empty-subtext {
  font-size: 13px;
  opacity: 0.7;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-avatar {
  width: 28px;
  height: 28px;
  border-radius: 4px;
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.message-role {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
}

.message-time {
  font-size: 11px;
  color: var(--text-muted);
}

.message-body {
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}

/* 输入区域 */
.input-area {
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
  padding: 12px 16px;
}

.input-toolbar {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.model-select {
  padding: 4px 8px;
  font-size: 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-primary);
  cursor: pointer;
  outline: none;
}

.model-select:hover {
  border-color: var(--accent);
}

.input-box {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.input-box textarea {
  flex: 1;
  padding: 10px 12px;
  font-size: 13px;
  line-height: 1.5;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  resize: none;
  outline: none;
  font-family: inherit;
}

.input-box textarea:focus {
  border-color: var(--accent);
}

.input-box textarea::placeholder {
  color: var(--text-muted);
}

.btn-send {
  width: 36px;
  height: 36px;
  border: none;
  background: var(--accent);
  color: white;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}

.btn-send:hover:not(:disabled) {
  background: var(--accent-hover);
}

.btn-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  width: 400px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.btn-close {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.btn-close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.modal-body {
  padding: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.form-group label .required {
  color: var(--error);
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px 10px;
  font-size: 13px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-primary);
  outline: none;
}

.form-group input:focus,
.form-group select:focus {
  border-color: var(--accent);
}

.form-group select option:disabled {
  color: var(--text-muted);
  opacity: 0.5;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
}

.btn-secondary,
.btn-primary {
  padding: 6px 14px;
  font-size: 12px;
  border-radius: 4px;
  cursor: pointer;
  border: none;
  transition: background 0.15s;
}

.btn-secondary {
  background: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: var(--bg-hover);
}

.btn-primary {
  background: var(--accent);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--accent-hover);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 滚动条样式 */
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
  background: #4a4a4e;
}
</style>
