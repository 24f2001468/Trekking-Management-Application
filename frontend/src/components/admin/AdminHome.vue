<template>
  <div>
    <div class="page-header">
      <h1>Dashboard Overview</h1>
    </div>

    <div v-if="loading" class="loading">Loading stats...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="stats-grid">
      
      <div class="stat-card glass-panel">
        <div class="stat-icon treks">🏔️</div>
        <div class="stat-content">
          <h3>Total Treks</h3>
          <p class="stat-value">{{ stats.total_treks }}</p>
        </div>
      </div>

      <div class="stat-card glass-panel">
        <div class="stat-icon users">👥</div>
        <div class="stat-content">
          <h3>Registered Users</h3>
          <p class="stat-value">{{ stats.total_users }}</p>
        </div>
      </div>

      <div class="stat-card glass-panel">
        <div class="stat-icon staff">👨‍💼</div>
        <div class="stat-content">
          <h3>Trek Staff</h3>
          <p class="stat-value">{{ stats.total_staff }}</p>
        </div>
      </div>

      <div class="stat-card glass-panel">
        <div class="stat-icon bookings">📅</div>
        <div class="stat-content">
          <h3>Total Bookings</h3>
          <p class="stat-value">{{ stats.total_bookings }}</p>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'AdminHome',
  setup() {
    const stats = ref({
      total_treks: 0,
      total_users: 0,
      total_staff: 0,
      total_bookings: 0
    })
    const loading = ref(true)
    const error = ref('')

    const fetchStats = async () => {
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch('http://localhost:5000/api/admin/dashboard_stats', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        if (!response.ok) throw new Error('Failed to load stats')
        const data = await response.json()
        stats.value = data
      } catch (err) {
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    onMounted(fetchStats)

    return { stats, loading, error }
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
.stat-icon.staff { background: rgba(245, 158, 11, 0.2); }
.stat-icon.bookings { background: rgba(168, 85, 247, 0.2); }

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

.loading, .error {
  padding: 2rem;
  text-align: center;
  background: var(--card-bg);
  border-radius: 12px;
}
.error { color: var(--danger); }
</style>
