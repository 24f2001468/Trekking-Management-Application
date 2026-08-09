<template>
  <div>
    <div class="page-header">
      <h1>All Bookings</h1>
      <div class="stats-row" v-if="!statsLoading">
        <span class="stat-chip">Total: {{ payStats.total_bookings }}</span>
        <span class="stat-chip chip-success">Paid: {{ payStats.paid }}</span>
        <span class="stat-chip chip-warning">Pending: {{ payStats.pending }}</span>
        <span class="stat-chip chip-danger">Failed: {{ payStats.failed }}</span>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading bookings...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else class="premium-table-wrapper">
      <table class="premium-table">
        <thead>
          <tr>
            <th>Booking ID</th>
            <th>Date</th>
            <th>Trek Name</th>
            <th>User</th>
            <th>Booking Status</th>
            <th>Payment</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in bookings" :key="b.id">
            <td data-label="ID">#{{ b.id }}</td>
            <td data-label="Date">{{ formatDate(b.booking_date) }}</td>
            <td data-label="Trek"><strong>{{ b.trek?.name }}</strong></td>
            <td data-label="User">{{ b.user?.username }}</td>
            <td data-label="Booking Status">
              <select
                v-model="b.status"
                @change="updateBookingStatus(b)"
                class="premium-input status-select"
              >
                <option value="Booked">Booked</option>
                <option value="Completed">Completed</option>
                <option value="Cancelled">Cancelled</option>
              </select>
            </td>
            <td data-label="Payment">
              <select
                v-model="b.payment_status"
                @change="updatePaymentStatus(b)"
                class="premium-input status-select"
              >
                <option value="Pending">Pending</option>
                <option value="Paid">Paid</option>
                <option value="Failed">Failed</option>
              </select>
            </td>
            <td data-label="Badges">
              <div style="display: flex; gap: 0.4rem; flex-wrap: wrap;">
                <span class="badge" 
                  :class="{
                    'badge-primary': b.status === 'Booked',
                    'badge-success': b.status === 'Completed',
                    'badge-danger': b.status === 'Cancelled'
                  }">
                  {{ b.status }}
                </span>
                <span class="badge" 
                  :class="{
                    'badge-warning': b.payment_status === 'Pending',
                    'badge-success': b.payment_status === 'Paid',
                    'badge-danger': b.payment_status === 'Failed'
                  }">
                  {{ b.payment_status }}
                </span>
              </div>
            </td>
          </tr>
          <tr v-if="bookings.length === 0">
            <td colspan="7" style="text-align: center; padding: 2rem;">No bookings found.</td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useToast } from '../../composables/useToast.js'

export default {
  name: 'AdminBookings',
  setup() {
    const bookings = ref([])
    const loading = ref(true)
    const error = ref('')
    const statsLoading = ref(true)
    const payStats = ref({ total_bookings: 0, paid: 0, pending: 0, failed: 0 })
    const { success, error: toastError } = useToast()

    const fetchBookings = async () => {
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch('/api/admin/bookings', {
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

    const fetchStats = async () => {
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch('/api/admin/stats/revenue', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (response.ok) payStats.value = await response.json()
      } catch (err) {
        console.error('Failed to load payment stats', err)
      } finally {
        statsLoading.value = false
      }
    }

    const updateBookingStatus = async (booking) => {
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch(`/api/admin/bookings/${booking.id}/status`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ status: booking.status })
        })
        const data = await response.json()
        if (!response.ok) {
          // revert to original from server data on failure
          throw new Error(data.msg || 'Failed to update booking status')
        }
        // Sync local state with server response
        const index = bookings.value.findIndex(b => b.id === data.id)
        if (index !== -1) bookings.value[index] = { ...bookings.value[index], ...data }
        success('Booking status updated.')
        fetchStats()
      } catch (err) {
        toastError(err.message)
        fetchBookings() // refresh to restore correct state
      }
    }

    const updatePaymentStatus = async (booking) => {
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch(`/api/admin/bookings/${booking.id}/payment`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ payment_status: booking.payment_status })
        })
        const data = await response.json()
        if (!response.ok) throw new Error(data.msg || 'Failed to update payment status')

        const index = bookings.value.findIndex(b => b.id === data.id)
        if (index !== -1) bookings.value[index] = { ...bookings.value[index], ...data }
        success('Payment status updated.')
        fetchStats()
      } catch (err) {
        toastError(err.message)
        fetchBookings() // refresh to restore correct state
      }
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      const d = new Date(dateStr)
      return d.toLocaleString()
    }

    onMounted(() => {
      fetchBookings()
      fetchStats()
    })

    return { bookings, loading, error, statsLoading, payStats, formatDate, updateBookingStatus, updatePaymentStatus }
  }
}
</script>

<style scoped>
.stats-row {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.stat-chip {
  padding: 0.35rem 0.9rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 600;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.12);
  color: var(--text-secondary);
}
.chip-success { background: rgba(16,185,129,0.15); border-color: rgba(16,185,129,0.35); color: #34d399; }
.chip-warning { background: rgba(245,158,11,0.15); border-color: rgba(245,158,11,0.35); color: #fbbf24; }
.chip-danger  { background: rgba(239,68,68,0.15);  border-color: rgba(239,68,68,0.35);  color: #f87171; }

.status-select {
  padding: 0.3rem 0.5rem;
  font-size: 0.8rem;
  width: auto;
  min-width: 110px;
}
</style>
