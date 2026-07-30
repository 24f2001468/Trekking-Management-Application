<template>
  <div>
    <div class="page-header">
      <h1>Welcome back, {{ username }}!</h1>
    </div>

    <div v-if="loading" class="loading">Loading dashboard...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else>
      <div class="stats-grid">
        <div class="stat-card glass-panel">
          <div class="stat-icon treks">📅</div>
          <div class="stat-content">
            <h3>Total Bookings</h3>
            <p class="stat-value">{{ bookings.length }}</p>
          </div>
        </div>
        
        <div class="stat-card glass-panel">
          <div class="stat-icon users">🏔️</div>
          <div class="stat-content">
            <h3>Completed Treks</h3>
            <p class="stat-value">{{ completedCount }}</p>
          </div>
        </div>
      </div>

      <div class="premium-table-wrapper" style="margin-top: 2rem;" v-if="upcomingBookings.length > 0">
        <h3 style="padding: 1rem 1.5rem; margin: 0; border-bottom: var(--glass-border);">Upcoming Adventures</h3>
        <table class="premium-table">
          <thead>
            <tr>
              <th>Trek Name</th>
              <th>Location</th>
              <th>Dates</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in upcomingBookings" :key="b.id">
              <td><strong>{{ b.trek?.name }}</strong></td>
              <td>{{ b.trek?.location }}</td>
              <td>{{ b.trek?.start_date }}</td>
              <td>
                <span class="badge badge-primary">{{ b.status }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div v-else-if="bookings.length === 0" style="margin-top: 2rem; text-align: center; padding: 3rem;" class="glass-panel">
        <h2>Ready for an adventure?</h2>
        <p style="color: var(--text-secondary); margin-bottom: 2rem;">You haven't booked any treks yet.</p>
        <router-link to="/trekker/browse" class="btn-premium btn-primary" style="text-decoration: none;">
          Browse Available Treks
        </router-link>
      </div>

    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'

export default {
  name: 'TrekkerHome',
  setup() {
    const bookings = ref([])
    const loading = ref(true)
    const error = ref('')
    const username = ref('')

    const fetchBookings = async () => {
      try {
        const userStr = localStorage.getItem('tma_user')
        if(userStr) {
          username.value = JSON.parse(userStr).username
        }
        
        const token = localStorage.getItem('tma_token')
        const response = await fetch('http://localhost:5000/api/trekker/bookings', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (!response.ok) throw new Error('Failed to load dashboard data')
        bookings.value = await response.json()
      } catch (err) {
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    const completedCount = computed(() => {
      return bookings.value.filter(b => b.status === 'Completed').length
    })

    const upcomingBookings = computed(() => {
      return bookings.value.filter(b => b.status === 'Booked')
    })

    onMounted(fetchBookings)

    return { bookings, loading, error, username, completedCount, upcomingBookings }
  }
}
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
}

.stat-icon.treks { background: rgba(59, 130, 246, 0.2); }
.stat-icon.users { background: rgba(16, 185, 129, 0.2); }

.stat-content h3 {
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-value {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
}
</style>
