<template>
  <div>
    <div class="page-header">
      <div>
        <h1>Dashboard Overview</h1>
        <p>Welcome back — here's what's happening today.</p>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading stats...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="stats-grid">

      <div class="stat-card glass-panel">
        <div class="stat-icon treks"><i class="bi bi-map-fill"></i></div>
        <div class="stat-content">
          <h3>Total Treks</h3>
          <p class="stat-value">{{ stats.total_treks }}</p>
        </div>
      </div>

      <div class="stat-card glass-panel">
        <div class="stat-icon users"><i class="bi bi-people-fill"></i></div>
        <div class="stat-content">
          <h3>Registered Users</h3>
          <p class="stat-value">{{ stats.total_users }}</p>
        </div>
      </div>

      <div class="stat-card glass-panel">
        <div class="stat-icon staff"><i class="bi bi-person-badge-fill"></i></div>
        <div class="stat-content">
          <h3>Trek Staff</h3>
          <p class="stat-value">{{ stats.total_staff }}</p>
        </div>
      </div>

      <div class="stat-card glass-panel">
        <div class="stat-icon bookings"><i class="bi bi-calendar-check-fill"></i></div>
        <div class="stat-content">
          <h3>Total Bookings</h3>
          <p class="stat-value">{{ stats.total_bookings }}</p>
        </div>
      </div>

    </div>

    <div class="glass-panel" style="margin-top:1.75rem;padding:1.5rem;">
      <h3 style="margin:0 0 1.1rem;font-size:1rem;font-weight:700;">Quick Actions</h3>
      <div style="display:flex;gap:.85rem;flex-wrap:wrap;">
        <a :href="reportUrl" target="_blank" class="btn-premium btn-success">
          <i class="bi bi-file-earmark-bar-graph-fill"></i> Download Monthly Report
        </a>
        <router-link to="/admin/analytics" class="btn-premium btn-outline">
          <i class="bi bi-bar-chart-fill"></i> View Analytics
        </router-link>
        <router-link to="/admin/treks" class="btn-premium btn-outline">
          <i class="bi bi-map-fill"></i> Manage Treks
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
export default {
  name: 'AdminHome',
  setup() {
    const stats = ref({ total_treks:0, total_users:0, total_staff:0, total_bookings:0 })
    const loading = ref(true), error = ref('')
    const reportUrl = '/api/admin/reports/monthly'
    const fetchStats = async () => {
      try {
        const res = await fetch('/api/admin/dashboard_stats', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('tma_token')}` }
        })
        if (!res.ok) throw new Error('Failed to load stats')
        stats.value = await res.json()
      } catch (e) { error.value = e.message }
      finally { loading.value = false }
    }
    onMounted(fetchStats)
    return { stats, loading, error, reportUrl }
  }
}
</script>
