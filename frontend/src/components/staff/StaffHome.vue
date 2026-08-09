<template>
  <div>
    <div class="page-header">
      <h1>My Staff Dashboard</h1>
    </div>

    <div v-if="loading" class="loading">Loading dashboard...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else class="stats-grid">
      
      <div class="stat-card glass-panel">
        <div class="stat-icon treks"><i class="bi bi-map-fill"></i></div>
        <div class="stat-content">
          <h3>Assigned Treks</h3>
          <p class="stat-value">{{ treks.length }}</p>
        </div>
      </div>

      <div class="stat-card glass-panel">
        <div class="stat-icon users"><i class="bi bi-people-fill"></i></div>
        <div class="stat-content">
          <h3>Total Trekkers</h3>
          <p class="stat-value">{{ totalTrekkers }}</p>
        </div>
      </div>

    </div>

    <div class="premium-table-wrapper" style="margin-top: 2rem;" v-if="treks.length > 0">
      <h3 style="padding: 1rem 1.5rem; margin: 0; border-bottom: var(--glass-border);">Recent Assigned Treks</h3>
      <table class="premium-table">
        <thead>
          <tr>
            <th>Trek Name</th>
            <th>Dates</th>
            <th>Status</th>
            <th>Registered</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in treks.slice(0, 5)" :key="t.id">
            <td><strong>{{ t.name }}</strong></td>
            <td>{{ t.start_date }} - {{ t.end_date }}</td>
            <td>
              <span class="badge" 
                :class="{
                  'badge-success': t.status === 'Open',
                  'badge-warning': t.status === 'Ongoing' || t.status === 'Pending',
                  'badge-danger': t.status === 'Closed',
                  'badge-primary': t.status === 'Completed'
                }">
                {{ t.status }}
              </span>
            </td>
            <td>{{ t.participants_count }} / {{ t.available_slots + t.participants_count }}</td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'

export default {
  name: 'StaffHome',
  setup() {
    const treks = ref([])
    const loading = ref(true)
    const error = ref('')

    const fetchTreks = async () => {
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch('/api/staff/treks', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        if (!response.ok) throw new Error('Failed to load dashboard data')
        treks.value = await response.json()
      } catch (err) {
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    const totalTrekkers = computed(() => {
      return treks.value.reduce((sum, trek) => sum + (trek.participants_count || 0), 0)
    })

    onMounted(fetchTreks)

    return { treks, loading, error, totalTrekkers }
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

.loading, .error {
  padding: 2rem;
  text-align: center;
  background: var(--card-bg);
  border-radius: 12px;
}
.error { color: var(--danger); }
</style>
