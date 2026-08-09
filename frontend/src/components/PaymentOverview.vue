<template>
  <div>
    <div class="page-header">
      <h1>Payment Overview</h1>
      <p style="color: var(--text-secondary); margin-top: 0.5rem;">Track and manage booking payment statuses.</p>
    </div>

    <!-- Stats Row -->
    <div class="stats-grid" v-if="!statsLoading">
      <div class="stat-card glass-panel">
        <div class="stat-icon" style="background: rgba(59,130,246,0.2);">📋</div>
        <div class="stat-content">
          <h3>Total Bookings</h3>
          <p class="stat-value">{{ stats.total_bookings }}</p>
        </div>
      </div>
      <div class="stat-card glass-panel">
        <div class="stat-icon" style="background: rgba(16,185,129,0.2);">✅</div>
        <div class="stat-content">
          <h3>Paid</h3>
          <p class="stat-value">{{ stats.paid }}</p>
        </div>
      </div>
      <div class="stat-card glass-panel">
        <div class="stat-icon" style="background: rgba(245,158,11,0.2);">[Wait]</div>
        <div class="stat-content">
          <h3>Pending</h3>
          <p class="stat-value">{{ stats.pending }}</p>
        </div>
      </div>
      <div class="stat-card glass-panel">
        <div class="stat-icon" style="background: rgba(239,68,68,0.2);">❌</div>
        <div class="stat-content">
          <h3>Failed</h3>
          <p class="stat-value">{{ stats.failed }}</p>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="glass-panel" style="padding: 1.25rem; margin: 2rem 0; display: flex; gap: 1rem; flex-wrap: wrap; align-items: center;">
      <select v-model="filterPayment" class="premium-input" style="width: 160px;">
        <option value="">All Payments</option>
        <option value="Pending">Pending</option>
        <option value="Paid">Paid</option>
        <option value="Failed">Failed</option>
      </select>
      <select v-model="filterStatus" class="premium-input" style="width: 160px;">
        <option value="">All Statuses</option>
        <option value="Booked">Booked</option>
        <option value="Completed">Completed</option>
        <option value="Cancelled">Cancelled</option>
      </select>
      <input type="text" v-model="searchUser" placeholder="Search by user..." class="premium-input" style="width: 200px;">
    </div>

    <div v-if="loading" class="loading">Loading bookings...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else class="premium-table-wrapper">
      <table class="premium-table">
        <thead>
          <tr>
            <th>#</th>
            <th>User</th>
            <th>Trek</th>
            <th>Booking Status</th>
            <th>Payment Status</th>
            <th>Booked On</th>
            <th>Update Payment</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in filteredBookings" :key="b.id">
            <td data-label="#">{{ b.id }}</td>
            <td data-label="User"><strong>{{ b.user?.username }}</strong></td>
            <td data-label="Trek">{{ b.trek?.name }}</td>
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
            <td data-label="Booked On">{{ formatDate(b.booking_date) }}</td>
            <td data-label="Update">
              <select
                :value="b.payment_status"
                @change="updatePayment(b, $event.target.value)"
                class="premium-input"
                style="padding: 0.3rem 0.5rem; font-size: 0.8rem; width: auto; min-width: 110px;"
              >
                <option value="Pending">Pending</option>
                <option value="Paid">Paid</option>
                <option value="Failed">Failed</option>
              </select>
            </td>
          </tr>
          <tr v-if="filteredBookings.length === 0">
            <td colspan="7" style="text-align: center; padding: 2rem;">No bookings match the filters.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '../composables/useToast.js'

export default {
  name: 'PaymentOverview',
  setup() {
    const bookings = ref([])
    const loading = ref(true)
    const error = ref('')
    const stats = ref({ total_bookings: 0, paid: 0, pending: 0, failed: 0 })
    const statsLoading = ref(true)
    const filterPayment = ref('')
    const filterStatus = ref('')
    const searchUser = ref('')
    const { success, error: toastError } = useToast()

    const fetchBookings = async () => {
      try {
        const token = localStorage.getItem('tma_token')
        const res = await fetch('/api/admin/bookings', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (!res.ok) throw new Error('Failed to load bookings')
        bookings.value = await res.json()
      } catch (err) {
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    const fetchStats = async () => {
      try {
        const token = localStorage.getItem('tma_token')
        const res = await fetch('/api/admin/stats/revenue', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) stats.value = await res.json()
      } catch (err) {
        console.error(err)
      } finally {
        statsLoading.value = false
      }
    }

    const updatePayment = async (booking, newStatus) => {
      if (newStatus === booking.payment_status) return
      try {
        const token = localStorage.getItem('tma_token')
        const res = await fetch(`/api/admin/bookings/${booking.id}/payment`, {
          method: 'PUT',
          headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({ payment_status: newStatus })
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.msg || 'Update failed')
        
        const index = bookings.value.findIndex(b => b.id === data.id)
        if (index !== -1) bookings.value[index] = { ...bookings.value[index], ...data }
        success(`Payment status set to ${newStatus}.`)
        fetchStats()
      } catch (err) {
        toastError(err.message)
      }
    }

    const filteredBookings = computed(() => {
      return bookings.value.filter(b => {
        if (filterPayment.value && b.payment_status !== filterPayment.value) return false
        if (filterStatus.value && b.status !== filterStatus.value) return false
        if (searchUser.value) {
          const q = searchUser.value.toLowerCase()
          if (!b.user?.username?.toLowerCase().includes(q)) return false
        }
        return true
      })
    })

    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleDateString()
    }

    onMounted(() => { fetchBookings(); fetchStats() })

    return { bookings, loading, error, stats, statsLoading, filterPayment, filterStatus, searchUser, filteredBookings, updatePayment, formatDate }
  }
}
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}
.stat-card {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  transition: transform 0.3s ease;
}
.stat-card:hover { transform: translateY(-4px); }
.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
}
.stat-content h3 {
  margin: 0 0 0.4rem 0;
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-weight: 500;
}
.stat-value {
  margin: 0;
  font-size: 1.85rem;
  font-weight: 700;
  color: var(--text-primary);
}
</style>
