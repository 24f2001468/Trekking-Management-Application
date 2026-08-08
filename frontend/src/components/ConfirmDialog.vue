<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="confirmState.visible" class="confirm-overlay" @click.self="cancel">
        <div class="confirm-dialog glass-panel" role="dialog" aria-modal="true">
          <div class="confirm-header">
            <h5 class="confirm-title">{{ confirmState.title }}</h5>
          </div>
          <div class="confirm-body">
            <p>{{ confirmState.message }}</p>
          </div>
          <div class="confirm-footer">
            <button class="btn-premium btn-cancel" @click="cancel">Cancel</button>
            <button class="btn-premium" :class="confirmState.confirmClass" @click="confirm">
              {{ confirmState.confirmLabel }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script>
import { useConfirm } from '../composables/useConfirm.js'

export default {
  name: 'ConfirmDialog',
  setup() {
    const { confirmState, confirm, cancel } = useConfirm()
    return { confirmState, confirm, cancel }
  }
}
</script>

<style scoped>
.confirm-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 1rem;
}

.confirm-dialog {
  width: 100%;
  max-width: 420px;
  border-radius: 16px;
  overflow: hidden;
  animation: popIn 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes popIn {
  from { opacity: 0; transform: scale(0.85); }
  to   { opacity: 1; transform: scale(1); }
}

.confirm-header {
  padding: 1.25rem 1.5rem 0.75rem;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}

.confirm-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
}

.confirm-body {
  padding: 1rem 1.5rem;
  color: var(--text-secondary);
  font-size: 0.95rem;
  line-height: 1.55;
}
.confirm-body p { margin: 0; }

.confirm-footer {
  padding: 1rem 1.5rem 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-cancel {
  background: rgba(255,255,255,0.08);
  color: var(--text-secondary);
  border: 1px solid rgba(255,255,255,0.1);
}
.btn-cancel:hover { background: rgba(255,255,255,0.14); color: var(--text-primary); }

/* Transition */
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.25s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
</style>
