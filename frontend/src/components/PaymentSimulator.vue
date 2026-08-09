<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="visible" class="pay-overlay" @click.self="cancel" role="dialog" aria-modal="true" aria-labelledby="pay-title">
        <div class="pay-modal glass-panel">

          <!-- Header -->
          <div class="pay-header">
            <h2 id="pay-title"><i class="bi bi-credit-card-fill"></i> Payment Simulation</h2>
            <button class="pay-close" @click="cancel" aria-label="Close">×</button>
          </div>

          <!-- Amount Banner -->
          <div class="pay-amount-banner">
            <span class="pay-label">Amount Due</span>
            <span class="pay-amount">$49.99</span>
            <span class="pay-for">{{ bookingRef?.trek?.name || 'Trek Booking' }}</span>
          </div>

          <!-- Step: Card Form -->
          <div v-if="step === 'form'" class="pay-body">
            <div class="form-group">
              <label>Card Number</label>
              <div class="card-input-wrap">
                <input
                  type="text"
                  v-model="card.number"
                  class="premium-input"
                  placeholder="1234 5678 9012 3456"
                  maxlength="19"
                  @input="formatCardNumber"
                  autocomplete="cc-number"
                >
                <span class="card-icon">{{ cardIcon }}</span>
              </div>
              <span class="form-error" v-if="errors.number">{{ errors.number }}</span>
            </div>

            <div class="pay-row">
              <div class="form-group">
                <label>Expiry</label>
                <input
                  type="text"
                  v-model="card.expiry"
                  class="premium-input"
                  placeholder="MM/YY"
                  maxlength="5"
                  @input="formatExpiry"
                  autocomplete="cc-exp"
                >
                <span class="form-error" v-if="errors.expiry">{{ errors.expiry }}</span>
              </div>
              <div class="form-group">
                <label>CVV</label>
                <input
                  type="password"
                  v-model="card.cvv"
                  class="premium-input"
                  placeholder="•••"
                  maxlength="4"
                  autocomplete="cc-csc"
                >
                <span class="form-error" v-if="errors.cvv">{{ errors.cvv }}</span>
              </div>
            </div>

            <div class="form-group">
              <label>Card Holder Name</label>
              <input
                type="text"
                v-model="card.name"
                class="premium-input"
                placeholder="Name on card"
                autocomplete="cc-name"
              >
              <span class="form-error" v-if="errors.name">{{ errors.name }}</span>
            </div>

            <!-- Simulation hint -->
            <div class="sim-hint">
              <span class="sim-badge">🧪 Simulation Mode</span>
              Use card number ending in <strong>0002</strong> to simulate failure.
              All other valid numbers will succeed.
            </div>

            <div class="pay-actions">
              <button class="btn-premium" @click="cancel" style="background:rgba(255,255,255,0.08);color:var(--text-secondary);">Cancel</button>
              <button class="btn-premium btn-primary" @click="processPayment" :disabled="processing">
                {{ processing ? 'Processing...' : 'Pay $49.99' }}
              </button>
            </div>
          </div>

          <!-- Step: Processing -->
          <div v-else-if="step === 'processing'" class="pay-state">
            <div class="spinner" aria-hidden="true"></div>
            <p>Processing your payment...</p>
          </div>

          <!-- Step: Success -->
          <div v-else-if="step === 'success'" class="pay-state pay-state--success">
            <div class="state-icon">✅</div>
            <h3>Payment Successful!</h3>
            <p>Your booking has been confirmed and payment recorded.</p>
            <div class="receipt-box">
              <div class="receipt-row"><span>Transaction ID</span><strong>TXN-{{ txnId }}</strong></div>
              <div class="receipt-row"><span>Amount Charged</span><strong>$49.99</strong></div>
              <div class="receipt-row"><span>Status</span><span class="badge badge-success">Paid</span></div>
            </div>
            <button class="btn-premium btn-primary" @click="confirm" style="margin-top:1.5rem; width:100%;">Done</button>
          </div>

          <!-- Step: Failed -->
          <div v-else-if="step === 'failed'" class="pay-state pay-state--failed">
            <div class="state-icon">❌</div>
            <h3>Payment Declined</h3>
            <p>{{ failReason }}</p>
            <div class="pay-actions" style="margin-top:1.5rem;">
              <button class="btn-premium" @click="retry" style="background:rgba(255,255,255,0.08);color:var(--text-secondary);">Try Again</button>
              <button class="btn-premium btn-danger" @click="cancel">Cancel</button>
            </div>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'PaymentSimulator',
  props: {
    visible: { type: Boolean, default: false },
    bookingRef: { type: Object, default: null }
  },
  emits: ['success', 'cancel'],
  setup(props, { emit }) {
    const step = ref('form')   // form | processing | success | failed
    const processing = ref(false)
    const txnId = ref('')
    const failReason = ref('')

    const card = ref({ number: '', expiry: '', cvv: '', name: '' })
    const errors = ref({})

    // Reset when dialog opens
    watch(() => props.visible, (v) => {
      if (v) {
        step.value = 'form'
        card.value = { number: '', expiry: '', cvv: '', name: '' }
        errors.value = {}
        txnId.value = ''
        failReason.value = ''
      }
    })

    const cardIcon = computed(() => {
      const n = card.value.number.replace(/\s/g, '')
      if (n.startsWith('4')) return 'Visa'
      if (n.startsWith('5')) return 'Mastercard'
      if (n.startsWith('3')) return 'Amex'
      return 'Card'
    })

    const formatCardNumber = (e) => {
      let val = e.target.value.replace(/\D/g, '').slice(0, 16)
      card.value.number = val.replace(/(.{4})/g, '$1 ').trim()
    }

    const formatExpiry = (e) => {
      let val = e.target.value.replace(/\D/g, '').slice(0, 4)
      if (val.length >= 3) val = val.slice(0, 2) + '/' + val.slice(2)
      card.value.expiry = val
    }

    const validate = () => {
      const errs = {}
      const num = card.value.number.replace(/\s/g, '')
      if (num.length < 13) errs.number = 'Enter a valid card number'
      if (!card.value.expiry.match(/^\d{2}\/\d{2}$/)) errs.expiry = 'Format: MM/YY'
      if (card.value.cvv.length < 3) errs.cvv = 'Enter 3–4 digit CVV'
      if (!card.value.name.trim()) errs.name = 'Card holder name is required'
      errors.value = errs
      return Object.keys(errs).length === 0
    }

    const processPayment = () => {
      if (!validate()) return

      step.value = 'processing'
      processing.value = true

      // Simulate async payment processing (1.5 – 2.5s)
      const delay = 1500 + Math.random() * 1000
      setTimeout(() => {
        processing.value = false
        const lastFour = card.value.number.replace(/\s/g, '').slice(-4)

        // Card ending in 0002 → simulated decline
        if (lastFour === '0002') {
          failReason.value = 'Your card was declined by the issuing bank. Please try a different card.'
          step.value = 'failed'
        } else {
          txnId.value = Math.random().toString(36).substr(2, 9).toUpperCase()
          step.value = 'success'
        }
      }, delay)
    }

    const retry = () => {
      step.value = 'form'
      errors.value = {}
    }

    const confirm = () => emit('success', { txnId: txnId.value })
    const cancel = () => emit('cancel')

    return {
      step, processing, txnId, failReason,
      card, errors, cardIcon,
      formatCardNumber, formatExpiry,
      processPayment, retry, confirm, cancel
    }
  }
}
</script>

<style scoped>
.pay-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.72);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10100;
  padding: 1rem;
}

.pay-modal {
  width: 100%;
  max-width: 460px;
  border-radius: 20px;
  overflow: hidden;
  animation: popIn 0.28s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes popIn {
  from { opacity: 0; transform: scale(0.88) translateY(20px); }
  to   { opacity: 1; transform: scale(1) translateY(0); }
}

.pay-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 1.5rem 0.75rem;
  border-bottom: 1px solid rgba(255,255,255,0.07);
}
.pay-header h2 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
}
.pay-close {
  background: rgba(255,255,255,0.08);
  border: none;
  color: var(--text-secondary);
  font-size: 1.4rem;
  width: 32px; height: 32px;
  border-radius: 8px;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  line-height: 1;
  transition: background 0.2s, color 0.2s;
}
.pay-close:hover { background: rgba(255,255,255,0.14); color: #f8fafc; }

.pay-amount-banner {
  background: linear-gradient(135deg, rgba(59,130,246,0.2), rgba(16,185,129,0.2));
  border-bottom: 1px solid rgba(255,255,255,0.07);
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
}
.pay-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.pay-amount {
  font-size: 2.4rem;
  font-weight: 800;
  background: linear-gradient(135deg, #60a5fa, #34d399);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.1;
}
.pay-for {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.pay-body {
  padding: 1.5rem;
}

.pay-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.card-input-wrap {
  position: relative;
}
.card-icon {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.8rem;
  color: var(--text-secondary);
  pointer-events: none;
}

.sim-hint {
  background: rgba(245,158,11,0.1);
  border: 1px solid rgba(245,158,11,0.3);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  font-size: 0.8rem;
  color: #fbbf24;
  margin: 0.5rem 0 1.25rem 0;
  line-height: 1.5;
}
.sim-badge {
  display: inline-block;
  background: rgba(245,158,11,0.2);
  border-radius: 4px;
  padding: 0.1rem 0.5rem;
  font-weight: 600;
  margin-right: 0.4rem;
  font-size: 0.75rem;
}

.pay-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

/* Processing / Success / Failed states */
.pay-state {
  padding: 2.5rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0.75rem;
}
.pay-state p {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin: 0;
  max-width: 300px;
}
.pay-state h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
}

.state-icon { font-size: 3rem; line-height: 1; }

.pay-state--success .state-icon { filter: drop-shadow(0 0 12px rgba(16,185,129,0.5)); }
.pay-state--failed  .state-icon { filter: drop-shadow(0 0 12px rgba(239,68,68,0.5)); }

.receipt-box {
  background: rgba(15,23,42,0.6);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  width: 100%;
  margin-top: 0.5rem;
}
.receipt-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 0.875rem;
}
.receipt-row:last-child { border-bottom: none; }
.receipt-row span:first-child { color: var(--text-secondary); }

/* Spinner */
.spinner {
  width: 48px; height: 48px;
  border: 3px solid rgba(59,130,246,0.2);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Transition */
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.25s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
</style>
