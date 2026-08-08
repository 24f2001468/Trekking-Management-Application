<template>
  <div>
    <div class="page-header">
      <div>
        <h1>Trek History</h1>
        <p>Your complete trekking journey — completed, cancelled, and active.</p>
      </div>
      <button @click="triggerExport" class="btn-premium btn-primary" :disabled="exporting">
        <i class="bi bi-download"></i> {{ exporting ? 'Exporting…' : 'Export CSV' }}
      </button>
    </div>

    <!-- Stats Strip -->
    <div class="stats-grid" style="margin-bottom:1.75rem;" v-if="!loading && !error">
      <div class="stat-card glass-panel">
        <div class="stat-icon treks"><i class="bi bi-calendar-check-fill"></i></div>
        <div class="stat-content"><h3>Total Bookings</h3><p class="stat-value">{{ bookings.length }}</p></div>
      </div>
      <div class="stat-card glass-panel">
        <div class="stat-icon users"><i class="bi bi-trophy-fill"></i></div>
        <div class="stat-content"><h3>Completed</h3><p class="stat-value">{{ completed }}</p></div>
      </div>
      <div class="stat-card glass-panel">
        <div class="stat-icon bookings"><i class="bi bi-hourglass-split"></i></div>
        <div class="stat-content"><h3>Active</h3><p class="stat-value">{{ active }}</p></div>
      </div>
      <div class="stat-card glass-panel">
        <div class="stat-icon staff"><i class="bi bi-x-circle-fill"></i></div>
        <div class="stat-content"><h3>Cancelled</h3><p class="stat-value">{{ cancelled }}</p></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="glass-panel" style="padding:1.1rem 1.5rem;margin-bottom:1.5rem;display:flex;gap:.85rem;flex-wrap:wrap;align-items:center;">
      <select v-model="filterStatus" class="premium-input" style="width:150px;">
        <option value="">All Statuses</option>
        <option value="Booked">Active</option>
        <option value="Completed">Completed</option>
        <option value="Cancelled">Cancelled</option>
      </select>
      <select v-model="filterPayment" class="premium-input" style="width:160px;">
        <option value="">All Payments</option>
        <option value="Pending">Pending</option>
        <option value="Paid">Paid</option>
        <option value="Failed">Failed</option>
      </select>
      <input type="text" v-model="searchTrek" placeholder="Search trek name…"
        class="premium-input" style="flex:1;min-width:160px;">
    </div>

    <div v-if="loading" class="loading">Loading history…</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else class="premium-table-wrapper">
      <table class="premium-table">
        <thead>
          <tr>
            <th>Booking Date</th>
            <th>Trek</th>
            <th>Location</th>
            <th>Dates</th>
            <th>Difficulty</th>
            <th>Booking</th>
            <th>Payment</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in filtered" :key="b.id">
            <td data-label="Booked">{{ fmt(b.booking_date) }}</td>
            <td data-label="Trek"><strong>{{ b.trek?.name }}</strong></td>
            <td data-label="Location">{{ b.trek?.location }}</td>
            <td data-label="Dates" style="font-size:.82rem;">
              {{ b.trek?.start_date }} → {{ b.trek?.end_date }}
            </td>
            <td data-label="Difficulty">
              <span class="badge"
                :class="{'badge-success':b.trek?.difficulty==='Easy','badge-warning':b.trek?.difficulty==='Moderate','badge-danger':b.trek?.difficulty==='Hard'}">
                {{ b.trek?.difficulty }}
              </span>
            </td>
            <td data-label="Booking">
              <span class="badge"
                :class="{'badge-primary':b.status==='Booked','badge-success':b.status==='Completed','badge-danger':b.status==='Cancelled'}">
                {{ b.status }}
              </span>
            </td>
            <td data-label="Payment">
              <span class="badge"
                :class="{'badge-warning':b.payment_status==='Pending','badge-success':b.payment_status==='Paid','badge-danger':b.payment_status==='Failed'}">
                {{ b.payment_status }}
              </span>
            </td>
          </tr>
          <tr v-if="filtered.length === 0">
            <td colspan="7" style="text-align:center;padding:2.5rem;color:var(--text-2);">
              No records match the selected filters.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '../../composables/useToast.js'

const API = 'http://localhost:5000'
const tok = () => localStorage.getItem('tma_token')

export default {
  name: 'TrekkerHistory',
  setup() {
    const bookings = ref([]), loading = ref(true), error = ref('')
    const filterStatus = ref(''), filterPayment = ref(''), searchTrek = ref('')
    const exporting = ref(false)
    const { success, error: toastError, info } = useToast()

    const fetchBookings = async () => {
      try {
        const r = await fetch(`${API}/api/trekker/bookings`, {
          headers: { Authorization: `Bearer ${tok()}` }
        })
        if (!r.ok) throw new Error('Failed to load history')
        bookings.value = await r.json()
      } catch (e) { error.value = e.message }
      finally { loading.value = false }
    }

    const filtered = computed(() => bookings.value.filter(b => {
      if (filterStatus.value && b.status !== filterStatus.value) return false
      if (filterPayment.value && b.payment_status !== filterPayment.value) return false
      if (searchTrek.value) {
        const q = searchTrek.value.toLowerCase()
        if (!b.trek?.name?.toLowerCase().includes(q)) return false
      }
      return true
    }))

    const completed = computed(() => bookings.value.filter(b => b.status === 'Completed').length)
    const active    = computed(() => bookings.value.filter(b => b.status === 'Booked').length)
    const cancelled = computed(() => bookings.value.filter(b => b.status === 'Cancelled').length)

    const triggerExport = async () => {
      exporting.value = true
      info('Generating CSV export…')
      try {
        const r = await fetch(`${API}/api/trekker/export`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${tok()}` }
        })
        const d = await r.json()
        if (!r.ok) throw new Error(d.msg || 'Export failed')
        if (d.state === 'SUCCESS') {
          downloadCSV(d.csv_data)
          success('CSV downloaded successfully!')
        }
      } catch (e) { toastError(e.message) }
      finally { exporting.value = false }
    }

    const downloadCSV = (csv) => {
      const blob = new Blob([csv], { type: 'text/csv' })
      const url  = URL.createObjectURL(blob)
      const a    = document.createElement('a')
      a.href = url; a.download = 'trekking-history.csv'; a.click()
      URL.revokeObjectURL(url)
    }

    const fmt = (d) => d ? new Date(d).toLocaleDateString() : '—'

    onMounted(fetchBookings)
    return { bookings, loading, error, filtered, completed, active, cancelled,
             filterStatus, filterPayment, searchTrek, exporting, triggerExport, fmt }
  }
}
</script>
