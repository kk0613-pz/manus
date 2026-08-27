<script setup>
defineProps({
  tasks: { type: Array, required: true },
  activeTaskId: { type: Number, required: true },
})

const emit = defineEmits(['select', 'open-file'])

const statusMap = {
  completed: { label: '已完成', class: 'status-completed' },
  running: { label: '进行中', class: 'status-running' },
  pending: { label: '待处理', class: 'status-pending' },
}

function getStatus(status) {
  return statusMap[status] || statusMap.pending
}
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h2>任务列表</h2>
      <button class="new-task-btn" title="新建任务">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
        </svg>
      </button>
    </div>

    <div class="task-list">
      <div
        v-for="task in tasks"
        :key="task.id"
        class="task-item"
        :class="{ active: task.id === activeTaskId }"
        @click="emit('select', task.id)"
      >
        <div class="task-main">
          <div class="task-title">{{ task.title }}</div>
          <div class="task-meta">
            <span class="status" :class="getStatus(task.status).class">
              {{ getStatus(task.status).label }}
            </span>
            <span class="time">{{ task.updatedAt }}</span>
          </div>
        </div>

        <div v-if="task.files.length" class="file-list">
          <button
            v-for="file in task.files"
            :key="file.id"
            class="file-item"
            @click.stop="emit('open-file', file)"
          >
            <svg class="file-icon" width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path
                d="M3 1h5l3 3v9a1 1 0 01-1 1H3a1 1 0 01-1-1V2a1 1 0 011-1z"
                stroke="currentColor"
                stroke-width="1.2"
              />
              <path d="M8 1v3h3" stroke="currentColor" stroke-width="1.2" />
            </svg>
            <span>{{ file.name }}</span>
          </button>
        </div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  background: var(--bg-secondary);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  border-bottom: 1px solid var(--border);
}

.sidebar-header h2 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.new-task-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  transition: all var(--transition);
}

.new-task-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.task-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.task-item {
  padding: 12px;
  border-radius: var(--radius);
  cursor: pointer;
  transition: all var(--transition);
  margin-bottom: 4px;
  border: 1px solid transparent;
}

.task-item:hover {
  background: var(--bg-hover);
}

.task-item.active {
  background: var(--bg-tertiary);
  border-color: var(--border-light);
}

.task-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 6px;
  line-height: 1.4;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}

.status-completed {
  background: rgba(34, 197, 94, 0.15);
  color: var(--success);
}

.status-running {
  background: rgba(99, 102, 241, 0.15);
  color: var(--accent-hover);
}

.status-pending {
  background: rgba(245, 158, 11, 0.15);
  color: var(--warning);
}

.time {
  font-size: 11px;
  color: var(--text-muted);
}

.file-list {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--text-secondary);
  text-align: left;
  transition: all var(--transition);
  width: 100%;
}

.file-item:hover {
  background: var(--bg-hover);
  color: var(--accent-hover);
}

.file-icon {
  flex-shrink: 0;
  opacity: 0.7;
}
</style>
