// Global Confirm Dialog Composable
// Returns a Promise that resolves to true (confirmed) or false (cancelled).
import { reactive } from 'vue'

const state = reactive({
  visible: false,
  title: 'Confirm',
  message: 'Are you sure?',
  confirmLabel: 'Confirm',
  confirmClass: 'btn-danger',
  resolve: null
})

/**
 * Show a confirm dialog and return a Promise<boolean>.
 * @param {Object} opts
 * @param {string} opts.title
 * @param {string} opts.message
 * @param {string} opts.confirmLabel
 * @param {string} opts.confirmClass  - Bootstrap btn class for confirm button
 */
function showConfirm({ title = 'Confirm', message = 'Are you sure?', confirmLabel = 'Confirm', confirmClass = 'btn-danger' } = {}) {
  state.title = title
  state.message = message
  state.confirmLabel = confirmLabel
  state.confirmClass = confirmClass
  state.visible = true
  return new Promise((resolve) => {
    state.resolve = resolve
  })
}

function confirm() {
  state.visible = false
  if (state.resolve) state.resolve(true)
}

function cancel() {
  state.visible = false
  if (state.resolve) state.resolve(false)
}

export function useConfirm() {
  return {
    confirmState: state,
    confirm,
    cancel,
    showConfirm
  }
}
