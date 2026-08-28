<script setup>
import { ref } from 'vue'

const props = defineProps({
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['send'])

const inputText = ref('')

function handleSend() {
  if (!inputText.value.trim() || props.loading) return
  emit('send', inputText.value)
  inputText.value = ''
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}
</script>

<template>
  <div class="chat-input-area">
    <div class="input-wrapper">
      <textarea
        v-model="inputText"
        class="input-field"
        placeholder="输入消息，Enter 发送，Shift+Enter 换行..."
        rows="3"
        :disabled="loading"
        @keydown="handleKeydown"
      />
      <div class="input-actions">
        <button
          class="send-btn"
          :disabled="!inputText.trim() || loading"
          @click="handleSend"
        >
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <path
              d="M16 2L8 10M16 2l-5 14-3-6-6-3 14-5z"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
          <span>发送</span>
        </button>
      </div>
    </div>
    <p class="input-hint">Manus AI 可能会产生错误，请核实重要信息。</p>
  </div>
</template>

<style scoped>
.chat-input-area {
  padding: 16px 24px 20px;
  border-top: 1px solid var(--border);
  background: var(--bg-secondary);
  flex-shrink: 0;
}

.input-wrapper {
  max-width: 780px;
  margin: 0 auto;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 16px;
  transition: border-color var(--transition);
}

.input-wrapper:focus-within {
  border-color: var(--accent);
}

.input-field {
  width: 100%;
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.5;
  resize: none;
  min-height: 60px;
}

.input-field::placeholder {
  color: var(--text-muted);
}

.input-field:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.send-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--accent);
  color: #fff;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 500;
  transition: all var(--transition);
}

.send-btn:hover:not(:disabled) {
  background: var(--accent-hover);
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.input-hint {
  max-width: 780px;
  margin: 8px auto 0;
  font-size: 11px;
  color: var(--text-muted);
  text-align: center;
}
</style>
