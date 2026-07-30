<template>
  <div>
    <div class="page-header">
      <h1>My Bookings</h1>
      <p style="color: var(--text-secondary); margin-top: 0.5rem;">Manage your trekking history and active bookings.</p>
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
            <td>{{ formatDate(b.booking_date) }}</td>
            <td>
              <strong>{{ b.trek?.name }}</strong><br>
              <small style="color: var(--text-secondary)">{{ b.trek?.start_date }} to {{ b.trek?.end_date }}</small>
            </td>
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
            <td>
              <button 
                v-if="b.status === 'Booked'"
                @click="cancelBooking(b.id)"
                class="btn-premium btn-danger" 
                style="padding: 0.4rem 0.8rem; font-size: 0.8rem;"
                :disabled="cancelling === b.id"
              >
                {{ cancelling === b.id ? 'Cancelling...' : 'Cancel' }}
              </button>
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
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'TrekkerBookings',
  setup() {
    const bookings = ref([])
    const loading = ref(true)
    const error = ref('')
    const cancelling = ref(null)

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
      if(!confirm("Are you sure you want to cancel this booking?")) return;
      
      cancelling.value = id
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch(`http://localhost:5000/api/trekker/bookings/${id}/cancel`, {
          method: 'PUT',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        const data = await response.json()
        if (!response.ok) throw new Error(data.msg || 'Failed to cancel booking')
        
        // Update local state
        const index = bookings.value.findIndex(b => b.id === data.id)
        if(index !== -1) bookings.value[index] = data
        alert("Booking cancelled successfully.")
      } catch (err) {
        alert(err.message)
      } finally {
        cancelling.value = null
      }
    }

    const formatDate = (dateStr) => {
      if(!dateStr) return '-'
      const d = new Date(dateStr)
      return d.toLocaleDateString()
    }

    onMounted(fetchBookings)

    return { bookings, loading, error, cancelling, cancelBooking, formatDate }
  }
}
</script>
