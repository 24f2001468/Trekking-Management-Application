<template>
  <div>
    <div class="page-header">
      <h1>All Bookings</h1>
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
            <th>Status</th>
            <th>Payment</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in bookings" :key="b.id">
            <td>#{{ b.id }}</td>
            <td>{{ formatDate(b.booking_date) }}</td>
            <td><strong>{{ b.trek?.name }}</strong></td>
            <td>{{ b.user?.username }}</td>
            <td>
              <span class="badge" 
                :class="{
                  'badge-primary': b.status === 'Booked',
                  'badge-success': b.status === 'Completed',
                  'badge-danger': b.status === 'Cancelled'
                }">
                {{ b.status }}
              </span>
            </td>
            <td>
              <span class="badge" 
                :class="{
                  'badge-warning': b.payment_status === 'Pending',
                  'badge-success': b.payment_status === 'Paid',
                  'badge-danger': b.payment_status === 'Failed'
                }">
                {{ b.payment_status }}
              </span>
            </td>
          </tr>
          <tr v-if="bookings.length === 0">
            <td colspan="6" style="text-align: center; padding: 2rem;">No bookings found.</td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'AdminBookings',
  setup() {
    const bookings = ref([])
    const loading = ref(true)
    const error = ref('')

    const fetchBookings = async () => {
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch('http://localhost:5000/api/admin/bookings', {
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

    const formatDate = (dateStr) => {
      if(!dateStr) return '-'
      const d = new Date(dateStr)
      return d.toLocaleString()
    }

    onMounted(fetchBookings)

    return { bookings, loading, error, formatDate }
  }
}
</script>
