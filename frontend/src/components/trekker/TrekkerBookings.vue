<template>
  <div>
    <div class="page-header" style="display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h1>My Bookings</h1>
        <p style="color: var(--text-secondary); margin-top: 0.5rem;">Manage your trekking history and active bookings.</p>
      </div>
      <button @click="triggerExport" class="btn-premium btn-primary" :disabled="exporting">
        {{ exporting ? 'Exporting...' : '📄 Export History (CSV)' }}
      </button>
    </div>

    <div v-if="loading" class="loading">Loading bookings...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else class="premium-table-wrapper">
      <table class="premium-table">
        <thead>
          <tr>
            <th>Booking Date</th>
            <th>Trek Details</th>
            <th>Booking Status</th>
            <th>Payment Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in bookings" :key="b.id">
            <td data-label="Date">{{ formatDate(b.booking_date) }}</td>
            <td data-label="Trek">
              <strong>{{ b.trek?.name }}</strong><br>
              <small style="color: var(--text-secondary)">{{ b.trek?.start_date }} to {{ b.trek?.end_date }}</small>
            </td>
            <td data-label="Booking Status">
              <span class="badge" 
                :class="{
                  'badge-primary': b.status === 'Booked',
                  'badge-success': b.status === 'Completed',
                  'badge-danger': b.status === 'Cancelled'
                }">
                {{ b.status }}
              </span>
            </td>
            <td data-label="Payment">
              <span class="badge" 
                :class="{
                  'badge-warning': b.payment_status === 'Pending',
                  'badge-success': b.payment_status === 'Paid',
                  'badge-danger': b.payment_status === 'Failed'
                }">
                {{ b.payment_status }}
              </span>
            </td>
            <td data-label="Actions">
              <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                <!-- Pay Now button – shown only for active booked + pending payment -->
                <button
                  v-if="b.status === 'Booked' && b.payment_status === 'Pending'"
                  @click="openPayment(b)"
                  class="btn-premium btn-success"
                  style="padding: 0.4rem 0.8rem; font-size: 0.8rem;"
                >
                  💳 Pay Now
                </button>
                <button 
                  v-if="b.status === 'Booked'"
                  @click="cancelBooking(b.id)"
                  class="btn-premium btn-danger" 
                  style="padding: 0.4rem 0.8rem; font-size: 0.8rem;"
                  :disabled="cancelling === b.id"
                >
                  {{ cancelling === b.id ? 'Cancelling...' : 'Cancel' }}
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="bookings.length === 0">
            <td colspan="5" style="text-align: center; padding: 3rem;">
              You have no bookings yet. 
              <br><br>
              <router-link to="/trekker/browse" class="btn-premium btn-primary" style="text-decoration: none;">
                Find a Trek
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Payment Simulator Modal -->
    <PaymentSimulator
      :visible="paymentModalOpen"
      :bookingRef="payingBooking"
      @success="onPaymentSuccess"
      @cancel="paymentModalOpen = false"
    />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useConfirm } from '../../composables/useConfirm.js'
import { useToast } from '../../composables/useToast.js'
import PaymentSimulator from '../PaymentSimulator.vue'

export default {
  name: 'TrekkerBookings',
  components: { PaymentSimulator },
  setup() {
    const bookings = ref([])
    const loading = ref(true)
    const error = ref('')
    const cancelling = ref(null)
    const exporting = ref(false)
    const { showConfirm } = useConfirm()
    const { success, error: toastError, info } = useToast()

    // Payment modal state
    const paymentModalOpen = ref(false)
    const payingBooking = ref(null)

    const openPayment = (booking) => {
      payingBooking.value = booking
      paymentModalOpen.value = true
    }

    const onPaymentSuccess = async ({ txnId }) => {
      paymentModalOpen.value = false
      try {
        const token = localStorage.getItem('tma_token')
        const res = await fetch(`http://localhost:5000/api/admin/bookings/${payingBooking.value.id}/pay`, {
          method: 'PUT',
          headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({ payment_status: 'Paid' })
        })
        if (res.ok) {
          const data = await res.json()
          const index = bookings.value.findIndex(b => b.id === data.id)
          if (index !== -1) bookings.value[index] = data
        } else {
          // fallback: update locally so UI reflects change immediately
          const index = bookings.value.findIndex(b => b.id === payingBooking.value.id)
          if (index !== -1) bookings.value[index] = { ...bookings.value[index], payment_status: 'Paid' }
        }
      } catch (e) {
        // network error: still update UI optimistically
        const index = bookings.value.findIndex(b => b.id === payingBooking.value.id)
        if (index !== -1) bookings.value[index] = { ...bookings.value[index], payment_status: 'Paid' }
      }
      success(`Payment confirmed! Transaction ID: ${txnId}`)
    }

    const triggerExport = async () => {
      exporting.value = true
      info('Generating your CSV export...')
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch('http://localhost:5000/api/trekker/export', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        const data = await response.json()
        if (!response.ok) throw new Error(data.msg || 'Failed to start export')

        // Handle synchronous export response (csv_data) or async task_id
        if (data.csv_data) {
          downloadCSV(data.csv_data)
          success('CSV export downloaded successfully!')
          exporting.value = false
        } else if (data.task_id) {
          pollExportStatus(data.task_id)
        } else {
          toastError('Unexpected export response')
          exporting.value = false
        }
      } catch (err) {
        toastError(err.message)
        exporting.value = false
      }
    }

    const pollExportStatus = async (taskId) => {
      const token = localStorage.getItem('tma_token')
      const checkStatus = async () => {
        try {
          const response = await fetch(`http://localhost:5000/api/trekker/export/${taskId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
          })
          const data = await response.json()
          
          if (data.state === 'SUCCESS') {
            downloadCSV(data.csv_data)
            success('CSV export downloaded successfully!')
            exporting.value = false
          } else if (data.state === 'FAILURE' || data.state === 'REVOKED') {
            toastError('Export failed: ' + data.msg)
            exporting.value = false
          } else {
            setTimeout(checkStatus, 1000)
          }
        } catch (err) {
          toastError('Error checking export status')
          exporting.value = false
        }
      }
      setTimeout(checkStatus, 1000)
    }

    const downloadCSV = (csvData) => {
      const blob = new Blob([csvData], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.setAttribute('href', url)
      a.setAttribute('download', 'trekking_history.csv')
      a.click()
      window.URL.revokeObjectURL(url)
    }

    const fetchBookings = async () => {
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch('http://localhost:5000/api/trekker/bookings', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (!response.ok) throw new Error('Failed to load bookings')
        bookings.value = await response.json()
      } catch (err) {
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    const cancelBooking = async (id) => {
      const confirmed = await showConfirm({
        title: 'Cancel Booking',
        message: 'Are you sure you want to cancel this booking? This action cannot be undone.',
        confirmLabel: 'Yes, Cancel',
        confirmClass: 'btn-danger'
      })
      if (!confirmed) return
      
      cancelling.value = id
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch(`http://localhost:5000/api/trekker/bookings/${id}/cancel`, {
          method: 'PUT',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        const data = await response.json()
        if (!response.ok) throw new Error(data.msg || 'Failed to cancel booking')
        
        const index = bookings.value.findIndex(b => b.id === data.id)
        if (index !== -1) bookings.value[index] = data
        success('Booking cancelled successfully.')
      } catch (err) {
        toastError(err.message)
      } finally {
        cancelling.value = null
      }
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      const d = new Date(dateStr)
      return d.toLocaleDateString()
    }

    onMounted(fetchBookings)

    return {
      bookings, loading, error, cancelling, cancelBooking, formatDate,
      triggerExport, exporting,
      paymentModalOpen, payingBooking, openPayment, onPaymentSuccess
    }
  }
}
</script>
