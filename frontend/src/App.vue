<script setup>
import { ref, computed } from 'vue'
import TaskSidebar from './components/TaskSidebar.vue'
import ChatArea from './components/ChatArea.vue'
import ChatInput from './components/ChatInput.vue'
import FilePanel from './components/FilePanel.vue'

const tasks = ref([
  {
    id: 1,
    title: '市场调研报告',
    status: 'completed',
    updatedAt: '2 分钟前',
    files: [
      { id: 'f1', name: 'market_analysis.md', type: 'markdown', content: '# 市场调研报告\n\n## 概述\n\n本报告针对 AI 助手市场进行了全面分析。\n\n## 主要发现\n\n1. **市场规模**：全球 AI 助手市场预计 2026 年达到 150 亿美元\n2. **增长趋势**：年复合增长率约 35%\n3. **主要玩家**：OpenAI、Anthropic、Google、Manus AI\n\n## 用户画像\n\n- 企业用户占比 62%\n- 个人开发者占比 28%\n- 其他 10%\n\n## 结论\n\nAI 助手市场仍处于高速增长期，垂直领域应用是主要机会。' },
      { id: 'f2', name: 'competitors.json', type: 'json', content: '{\n  "competitors": [\n    { "name": "ChatGPT", "marketShare": 45 },\n    { "name": "Claude", "marketShare": 25 },\n    { "name": "Gemini", "marketShare": 18 },\n    { "name": "Manus AI", "marketShare": 12 }\n  ]\n}' },
    ],
  },
  {
    id: 2,
    title: '网站原型设计',
    status: 'running',
    updatedAt: '进行中',
    files: [
      { id: 'f3', name: 'wireframe.html', type: 'html', content: '<!DOCTYPE html>\n<html>\n<head>\n  <title>Landing Page</title>\n</head>\n<body>\n  <header>\n    <h1>Welcome to Our Product</h1>\n  </header>\n  <main>\n    <section class="hero">\n      <p>AI-powered solutions for everyone</p>\n    </section>\n  </main>\n</body>\n</html>' },
    ],
  },
  {
    id: 3,
    title: '数据分析脚本',
    status: 'pending',
    updatedAt: '1 小时前',
    files: [],
  },
])

const activeTaskId = ref(1)

const messages = ref([
  {
    id: 1,
    role: 'assistant',
    content: '你好！我是 Manus AI 助手。我可以帮你完成各种任务，包括研究、写作、编程和数据分析。请告诉我你需要什么帮助？',
    timestamp: '10:30',
  },
])

const selectedFile = ref(null)
const panelOpen = ref(false)
const isLoading = ref(false)
const loadingPhase = ref('planning')

function parseSSEChunk(buffer, onEvent) {
  const parts = buffer.split('\n\n')
  const rest = parts.pop() || ''

  for (const part of parts) {
    const line = part.trim()
    if (!line.startsWith('data: ')) continue
    try {
      onEvent(JSON.parse(line.slice(6)))
    } catch (e) {
      console.error('SSE parse error', e)
    }
  }

  return rest
}

function updateAssistantTodos(assistantMsg, updater) {
  assistantMsg.todos = assistantMsg.todos.map((todo) => {
    const next = updater(todo)
    return next || todo
  })
  messages.value = [...messages.value]
}

function openFile(file) {
  selectedFile.value = file
  panelOpen.value = true
}

async function sendMessage(text) {
  if (!text.trim()) return

  const now = new Date()
  const timestamp = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  const content = text.trim()

  messages.value.push({
    id: Date.now(),
    role: 'user',
    content,
    timestamp,
  })

  isLoading.value = true
  loadingPhase.value = 'planning'

  let assistantMsg = null

  try {
    const res = await fetch('/api/message/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    })

    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}))
      throw new Error(errBody.detail || `请求失败: ${res.status}`)
    }

    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      buffer = parseSSEChunk(buffer, (event) => {
        if (event.type === 'planning') {
          loadingPhase.value = 'planning'
        }

        if (event.type === 'todos') {
          loadingPhase.value = 'executing'
          assistantMsg = {
            id: Date.now() + 1,
            role: 'assistant',
            content: '',
            analysis: event.analysis || '',
            todos: (event.todos || []).map((todo) => ({ ...todo })),
            timestamp,
          }
          messages.value.push(assistantMsg)
        }

        if (event.type === 'todo_start' && assistantMsg) {
          updateAssistantTodos(assistantMsg, (todo) =>
            todo.id == event.id ? { ...todo, status: 'running' } : null
          )
        }

        if (event.type === 'todo_done' && assistantMsg) {
          updateAssistantTodos(assistantMsg, (todo) =>
            todo.id == event.id ? { ...todo, status: 'done' } : null
          )
        }

        if (event.type === 'complete' && assistantMsg) {
          assistantMsg.content = event.content || ''
          messages.value = [...messages.value]
        }

        if (event.type === 'error') {
          throw new Error(event.message || '处理失败')
        }
      })
    }
  } catch (err) {
    if (assistantMsg) {
      assistantMsg.content = `处理失败：${err.message || '请确认后端已启动并配置 API Key。'}`
    } else {
      messages.value.push({
        id: Date.now() + 1,
        role: 'assistant',
        content: `消息发送失败：${err.message || '请确认后端已启动并配置 API Key。'}`,
        timestamp,
      })
    }
    console.error(err)
  } finally {
    isLoading.value = false
    loadingPhase.value = 'planning'
  }
}

const activeTask = computed(() =>
  tasks.value.find((t) => t.id === activeTaskId.value)
)

function selectTask(id) {
  activeTaskId.value = id
  selectedFile.value = null
  panelOpen.value = false
}

function closePanel() {
  panelOpen.value = false
}
</script>

<template>
  <div class="app-layout">
    <TaskSidebar
      :tasks="tasks"
      :active-task-id="activeTaskId"
      @select="selectTask"
      @open-file="openFile"
    />

    <main class="main-content">
      <header class="main-header">
        <div class="header-left">
          <div class="logo">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5" />
              <path d="M8 12h8M12 8v8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
            </svg>
            <span>Manus AI</span>
          </div>
          <span v-if="activeTask" class="task-badge">{{ activeTask.title }}</span>
        </div>
      </header>

      <ChatArea :messages="messages" :loading="isLoading" :loading-phase="loadingPhase" />

      <ChatInput :loading="isLoading" @send="sendMessage" />
    </main>

    <FilePanel
      :file="selectedFile"
      :open="panelOpen"
      @close="closePanel"
    />
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: var(--bg-primary);
}

.main-header {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-secondary);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 15px;
  color: var(--text-primary);
}

.logo svg {
  color: var(--accent);
}

.task-badge {
  font-size: 13px;
  color: var(--text-secondary);
  background: var(--bg-tertiary);
  padding: 4px 12px;
  border-radius: 20px;
  border: 1px solid var(--border);
}
</style>
