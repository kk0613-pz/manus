<script setup>
import { computed } from 'vue'

const props = defineProps({
  file: { type: Object, default: null },
  open: { type: Boolean, default: false },
})

defineEmits(['close'])

const typeLabel = computed(() => {
  if (!props.file) return ''
  const map = {
    markdown: 'Markdown',
    json: 'JSON',
    html: 'HTML',
    js: 'JavaScript',
    css: 'CSS',
    txt: 'Text',
  }
  return map[props.file.type] || props.file.type.toUpperCase()
})
</script>

<template>
  <Transition name="panel">
    <div v-if="open && file" class="panel-overlay" @click.self="$emit('close')">
      <aside class="file-panel">
        <header class="panel-header">
          <div class="panel-title">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path
                d="M3 1h6l4 4v10a1 1 0 01-1 1H3a1 1 0 01-1-1V2a1 1 0 011-1z"
                stroke="currentColor"
                stroke-width="1.2"
              />
              <path d="M9 1v4h4" stroke="currentColor" stroke-width="1.2" />
            </svg>
            <span>{{ file.name }}</span>
            <span class="type-badge">{{ typeLabel }}</span>
          </div>
          <button class="close-btn" @click="$emit('close')">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M4 4l10 10M14 4L4 14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
            </svg>
          </button>
        </header>

        <div class="panel-body">
          <pre class="file-content"><code>{{ file.content }}</code></pre>
        </div>

        <footer class="panel-footer">
          <button class="action-btn">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M7 1v8M4 6l3 3 3-3M2 11h10" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            下载
          </button>
          <button class="action-btn">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <rect x="2" y="2" width="8" height="8" rx="1" stroke="currentColor" stroke-width="1.2" />
              <path d="M4 10h8v2H6a2 2 0 01-2-2v-8H4" stroke="currentColor" stroke-width="1.2" />
            </svg>
            复制
          </button>
        </footer>
      </aside>
    </div>
  </Transition>
</template>

<style scoped>
.panel-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 100;
  display: flex;
  justify-content: flex-end;
}

.file-panel {
  width: var(--panel-width);
  max-width: 90vw;
  height: 100%;
  background: var(--bg-secondary);
  border-left: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow);
}

.panel-header {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  min-width: 0;
}

.panel-title span:first-of-type {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.type-badge {
  font-size: 10px;
  padding: 2px 6px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--text-muted);
  flex-shrink: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  transition: all var(--transition);
  flex-shrink: 0;
}

.close-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.panel-body {
  flex: 1;
  overflow: auto;
  padding: 16px;
}

.file-content {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-word;
  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
}

.panel-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--border);
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  font-size: 12px;
  color: var(--text-secondary);
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  transition: all var(--transition);
}

.action-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.panel-enter-active,
.panel-leave-active {
  transition: opacity var(--transition);
}

.panel-enter-active .file-panel,
.panel-leave-active .file-panel {
  transition: transform var(--transition);
}

.panel-enter-from,
.panel-leave-to {
  opacity: 0;
}

.panel-enter-from .file-panel,
.panel-leave-to .file-panel {
  transform: translateX(100%);
}
</style>
