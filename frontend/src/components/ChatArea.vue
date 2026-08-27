<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  messages: { type: Array, required: true },
  loading: { type: Boolean, default: false },
})

const chatContainer = ref(null)

watch(
  () => [props.messages.length, props.loading],
  async () => {
    await nextTick()
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  }
)
</script>

<template>
  <div ref="chatContainer" class="chat-area">
    <div class="chat-messages">
      <div
        v-for="msg in messages"
        :key="msg.id"
        class="message-row"
        :class="msg.role"
      >
        <div v-if="msg.role === 'assistant'" class="avatar assistant-avatar">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5" />
            <path d="M8 12h8M12 8v8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
          </svg>
        </div>

        <div class="message-bubble" :class="msg.role">
          <div class="message-content">{{ msg.content }}</div>
          <div class="message-time">{{ msg.timestamp }}</div>
        </div>

        <div v-if="msg.role === 'user'" class="avatar user-avatar">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="1.5" />
            <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
          </svg>
        </div>
      </div>

      <div v-if="loading" class="message-row assistant">
        <div class="avatar assistant-avatar">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5" />
            <path d="M8 12h8M12 8v8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
          </svg>
        </div>

        <div class="message-bubble assistant thinking-bubble">
          <div class="thinking-text">
            规划中
            <span class="thinking-dots">
              <span class="dot">.</span>
              <span class="dot">.</span>
              <span class="dot">.</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.chat-messages {
  max-width: 780px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message-row {
  display: flex;
  align-items: flex-end;
  gap: 10px;
}

.message-row.user {
  justify-content: flex-end;
}

.message-row.assistant {
  justify-content: flex-start;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.assistant-avatar {
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  color: var(--accent);
}

.user-avatar {
  background: var(--user-bubble);
  color: #fff;
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: var(--radius);
  line-height: 1.6;
}

.message-bubble.user {
  background: var(--user-bubble);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.message-bubble.assistant {
  background: var(--assistant-bubble);
  border: 1px solid var(--border);
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
}

.message-content {
  font-size: 14px;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-time {
  font-size: 11px;
  margin-top: 6px;
  opacity: 0.6;
}

.message-bubble.user .message-time {
  text-align: right;
}

.thinking-bubble {
  min-width: 100px;
}

.thinking-text {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: var(--text-secondary);
}

.thinking-dots {
  display: inline-flex;
  align-items: flex-end;
  margin-left: 1px;
  height: 1em;
}

.thinking-dots .dot {
  display: inline-block;
  font-size: 18px;
  line-height: 1;
  font-weight: 700;
  animation: dot-bounce 1.4s infinite ease-in-out both;
}

.thinking-dots .dot:nth-child(1) {
  animation-delay: 0s;
}

.thinking-dots .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.thinking-dots .dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dot-bounce {
  0%,
  80%,
  100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  40% {
    transform: translateY(-6px);
    opacity: 1;
  }
}
</style>
