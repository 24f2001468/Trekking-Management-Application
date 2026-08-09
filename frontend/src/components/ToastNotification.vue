<template>
  <Teleport to="body">
    <div class="toast-container" aria-live="polite" aria-atomic="true">
      <TransitionGroup name="toast-anim" tag="div">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="tma-toast"
          :class="[`tma-toast--${toast.type}`, { 'tma-toast--hide': !toast.visible }]"
          role="alert"
        >
          <span class="tma-toast__icon">{{ typeIcon(toast.type) }}</span>
          <span class="tma-toast__msg">{{ toast.message }}</span>
          <button class="tma-toast__close" @click="dismiss(toast.id)" aria-label="Close">&times;</button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script>
import { useToast } from '../composables/useToast.js'

export default {
  name: 'ToastNotification',
  setup() {
    const { toasts, dismiss } = useToast()

    const typeIcon = (type) => {
      const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' }
      return icons[type] || 'ℹ️'
    }

    return { toasts, dismiss, typeIcon }
  }
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 1.25rem;
  right: 1.25rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-width: 380px;
  width: calc(100vw - 2.5rem);
  pointer-events: none;
}

.tma-toast {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-radius: 12px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.35);
  border-left: 4px solid transparent;
  font-size: 0.925rem;
  font-weight: 500;
  pointer-events: all;
  transition: opacity 0.35s ease, transform 0.35s ease;
}

.tma-toast--success { background: rgba(16, 185, 129, 0.18); border-color: #10b981; color: #d1fae5; }
.tma-toast--error   { background: rgba(239, 68, 68, 0.18);  border-color: #ef4444; color: #fee2e2; }
.tma-toast--warning { background: rgba(245, 158, 11, 0.18); border-color: #f59e0b; color: #fef3c7; }
.tma-toast--info    { background: rgba(59, 130, 246, 0.18); border-color: #3b82f6; color: #dbeafe; }

.tma-toast--hide { opacity: 0; transform: translateX(20px); }

.tma-toast__icon { font-size: 1.1rem; flex-shrink: 0; margin-top: 0.05rem; }
.tma-toast__msg  { flex: 1; line-height: 1.4; }
.tma-toast__close {
  background: none;
  border: none;
  color: inherit;
  font-size: 1.25rem;
  cursor: pointer;
  opacity: 0.7;
  padding: 0;
  line-height: 1;
  flex-shrink: 0;
}
.tma-toast__close:hover { opacity: 1; }

/* TransitionGroup animations */
.toast-anim-enter-active { animation: slideInRight 0.35s ease; }
.toast-anim-leave-active { animation: slideOutRight 0.35s ease forwards; }

@keyframes slideInRight {
  from { opacity: 0; transform: translateX(60px); }
  to   { opacity: 1; transform: translateX(0); }
}
@keyframes slideOutRight {
  from { opacity: 1; transform: translateX(0); }
  to   { opacity: 0; transform: translateX(60px); }
}
</style>
