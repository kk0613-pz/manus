<script setup>
defineProps({
  todos: { type: Array, default: () => [] },
})
</script>

<template>
  <div v-if="todos.length" class="todo-list">
    <div class="todo-header">执行清单</div>
    <div
      v-for="todo in todos"
      :key="todo.id"
      class="todo-item"
      :class="todo.status"
    >
      <span class="todo-check">
        <svg v-if="todo.status === 'done'" width="14" height="14" viewBox="0 0 14 14" fill="none">
          <path d="M2 7l3 3 7-7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <span v-else-if="todo.status === 'running'" class="todo-spinner" />
        <span v-else class="todo-empty" />
      </span>
      <div class="todo-body">
        <div class="todo-title">{{ todo.title }}</div>
        <div v-if="todo.description" class="todo-desc">{{ todo.description }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.todo-list {
  margin-top: 4px;
}

.todo-header {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 10px;
  letter-spacing: 0.02em;
}

.todo-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid var(--border);
}

.todo-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.todo-check {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 1.5px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 1px;
  color: var(--success);
}

.todo-item.done .todo-check {
  background: rgba(34, 197, 94, 0.15);
  border-color: var(--success);
}

.todo-item.running .todo-check {
  border-color: var(--accent);
}

.todo-empty {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-muted);
  opacity: 0.5;
}

.todo-spinner {
  width: 10px;
  height: 10px;
  border: 1.5px solid var(--border-light);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.todo-body {
  min-width: 0;
}

.todo-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  line-height: 1.4;
}

.todo-item.done .todo-title {
  color: var(--text-secondary);
  text-decoration: line-through;
  text-decoration-color: var(--text-muted);
}

.todo-desc {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
  line-height: 1.4;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
