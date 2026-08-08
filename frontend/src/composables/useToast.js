// Global Toast Notification Composable
// Provides a reactive singleton that any component can import and use.
import { reactive } from 'vue'

const state = reactive({
  toasts: []
})

let idCounter = 0

/**
 * Show a toast notification.
 * @param {string} message  - Text to display
 * @param {'success'|'error'|'warning'|'info'} type - Toast type
 * @param {number} duration - Auto-dismiss in milliseconds (default 4000)
 */
function showToast(message, type = 'info', duration = 4000) {
  const id = ++idCounter
  state.toasts.push({ id, message, type, visible: true })
  setTimeout(() => dismissToast(id), duration)
}

function dismissToast(id) {
  const toast = state.toasts.find(t => t.id === id)
  if (toast) toast.visible = false
  // Remove from DOM after fade-out animation
  setTimeout(() => {
    const idx = state.toasts.findIndex(t => t.id === id)
    if (idx !== -1) state.toasts.splice(idx, 1)
  }, 400)
}

export function useToast() {
  return {
    toasts: state.toasts,
    toast: showToast,
    success: (msg, dur) => showToast(msg, 'success', dur),
    error:   (msg, dur) => showToast(msg, 'error',   dur),
    warning: (msg, dur) => showToast(msg, 'warning', dur),
    info:    (msg, dur) => showToast(msg, 'info',    dur),
    dismiss: dismissToast
  }
}
