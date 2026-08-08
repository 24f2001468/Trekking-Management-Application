<template>
  <div>
    <div class="page-header">
      <h1>Analytics</h1>
      <p style="color: var(--text-secondary); margin-top: 0.25rem;">Trek participation statistics and booking trends</p>
    </div>

    <div v-if="loading" class="loading">Loading analytics...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else>

      <!-- ── Row 1: Monthly Bookings Trend + Monthly Participation ── -->
      <div class="charts-row">

        <div class="chart-card glass-panel">
          <div class="chart-header">
            <h3>📈 Monthly Booking Trend</h3>
            <span class="chart-sub">Bookings created over the last 12 months</span>
          </div>
          <div class="chart-body">
            <Line :data="monthlyBookingsData" :options="lineOptions" />
          </div>
        </div>

        <div class="chart-card glass-panel">
          <div class="chart-header">
            <h3>👥 Monthly Unique Participants</h3>
            <span class="chart-sub">Distinct trekkers active per month</span>
          </div>
          <div class="chart-body">
            <Bar :data="monthlyParticipationData" :options="barOptions" />
          </div>
        </div>

      </div>

      <!-- ── Row 2: Top Treks (horizontal bar) ── -->
      <div class="chart-card glass-panel" style="margin-bottom: 2rem;">
        <div class="chart-header">
          <h3>🏆 Most Popular Treks</h3>
          <span class="chart-sub">Ranked by confirmed participant count</span>
        </div>
        <div class="chart-body chart-body--tall">
          <Bar :data="topTreksData" :options="topTreksOptions" />
        </div>
      </div>

      <!-- ── Row 3: Doughnut charts ── -->
      <div class="charts-row charts-row--3">

        <div class="chart-card glass-panel">
          <div class="chart-header">
            <h3>⛰️ Difficulty Distribution</h3>
            <span class="chart-sub">Bookings by trek difficulty</span>
          </div>
          <div class="chart-body chart-body--sm">
            <Doughnut :data="difficultyData" :options="doughnutOptions" />
          </div>
        </div>

        <div class="chart-card glass-panel">
          <div class="chart-header">
            <h3>📋 Booking Status</h3>
            <span class="chart-sub">Overall booking state breakdown</span>
          </div>
          <div class="chart-body chart-body--sm">
            <Doughnut :data="bookingStatusData" :options="doughnutOptions" />
          </div>
        </div>

        <div class="chart-card glass-panel">
          <div class="chart-header">
            <h3>💳 Payment Status</h3>
            <span class="chart-sub">Payment completion breakdown</span>
          </div>
          <div class="chart-body chart-body--sm">
            <Doughnut :data="paymentData" :options="doughnutOptions" />
          </div>
        </div>

      </div>

      <!-- ── Row 4: Trek Status Overview ── -->
      <div class="chart-card glass-panel">
        <div class="chart-header">
          <h3>🗂️ Trek Status Overview</h3>
          <span class="chart-sub">Distribution of treks across all lifecycle statuses</span>
        </div>
        <div class="chart-body">
          <Bar :data="trekStatusData" :options="trekStatusOptions" />
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { Bar, Line, Doughnut } from 'vue-chartjs'
import { PALETTE, PALETTE_ALPHA, PIE_COLORS, PIE_COLORS_ALPHA, darkScales } from '../../composables/useChartDefaults.js'

export default {
  name: 'AdminAnalytics',
  components: { Bar, Line, Doughnut },
  setup() {
    const data = ref(null)
    const loading = ref(true)
    const error = ref('')

    const fetchAnalytics = async () => {
      try {
        const token = localStorage.getItem('tma_token')
        const res = await fetch('http://localhost:5000/api/analytics/admin/overview', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (!res.ok) throw new Error('Failed to load analytics')
        data.value = await res.json()
      } catch (err) {
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    // ── Monthly Bookings Line Chart ──
    const monthlyBookingsData = computed(() => {
      if (!data.value) return { labels: [], datasets: [] }
      const rows = data.value.monthly_bookings
      return {
        labels: rows.map(r => r.month),
        datasets: [{
          label: 'Bookings',
          data: rows.map(r => r.bookings),
          borderColor: PALETTE.blue,
          backgroundColor: PALETTE.blue.replace(', 1)', ', 0.15)'),
          fill: true,
          tension: 0.4,
          pointBackgroundColor: PALETTE.blue,
          pointRadius: 4,
          pointHoverRadius: 6,
        }]
      }
    })

    // ── Monthly Participation Bar Chart ──
    const monthlyParticipationData = computed(() => {
      if (!data.value) return { labels: [], datasets: [] }
      const rows = data.value.monthly_participation
      return {
        labels: rows.map(r => r.month),
        datasets: [{
          label: 'Unique Participants',
          data: rows.map(r => r.participants),
          backgroundColor: PALETTE.green.replace(', 1)', ', 0.7)'),
          borderColor: PALETTE.green,
          borderWidth: 2,
          borderRadius: 6,
          borderSkipped: false,
        }]
      }
    })

    // ── Top Treks Horizontal Bar ──
    const topTreksData = computed(() => {
      if (!data.value) return { labels: [], datasets: [] }
      const rows = data.value.top_treks
      return {
        labels: rows.map(r => r.name),
        datasets: [{
          label: 'Participants',
          data: rows.map(r => r.participants),
          backgroundColor: rows.map((_, i) => PIE_COLORS[i % PIE_COLORS.length].replace(', 1)', ', 0.75)')),
          borderColor: rows.map((_, i) => PIE_COLORS[i % PIE_COLORS.length]),
          borderWidth: 1,
          borderRadius: 6,
          borderSkipped: false,
        }]
      }
    })

    // ── Difficulty Doughnut ──
    const difficultyData = computed(() => {
      if (!data.value) return { labels: [], datasets: [] }
      const dist = data.value.difficulty_distribution
      const labels = Object.keys(dist)
      const colorMap = { Easy: PALETTE.green, Moderate: PALETTE.amber, Hard: PALETTE.red }
      return {
        labels,
        datasets: [{
          data: labels.map(l => dist[l]),
          backgroundColor: labels.map(l => (colorMap[l] || PALETTE.blue).replace(', 1)', ', 0.75)')),
          borderColor: labels.map(l => colorMap[l] || PALETTE.blue),
          borderWidth: 2,
          hoverOffset: 8,
        }]
      }
    })

    // ── Booking Status Doughnut ──
    const bookingStatusData = computed(() => {
      if (!data.value) return { labels: [], datasets: [] }
      const dist = data.value.booking_status_distribution
      const colorMap = { Booked: PALETTE.blue, Completed: PALETTE.green, Cancelled: PALETTE.red }
      const labels = Object.keys(dist)
      return {
        labels,
        datasets: [{
          data: labels.map(l => dist[l]),
          backgroundColor: labels.map(l => (colorMap[l] || PALETTE.purple).replace(', 1)', ', 0.75)')),
          borderColor: labels.map(l => colorMap[l] || PALETTE.purple),
          borderWidth: 2,
          hoverOffset: 8,
        }]
      }
    })

    // ── Payment Doughnut ──
    const paymentData = computed(() => {
      if (!data.value) return { labels: [], datasets: [] }
      const dist = data.value.payment_distribution
      const colorMap = { Pending: PALETTE.amber, Paid: PALETTE.green, Failed: PALETTE.red }
      const labels = Object.keys(dist)
      return {
        labels,
        datasets: [{
          data: labels.map(l => dist[l]),
          backgroundColor: labels.map(l => (colorMap[l] || PALETTE.cyan).replace(', 1)', ', 0.75)')),
          borderColor: labels.map(l => colorMap[l] || PALETTE.cyan),
          borderWidth: 2,
          hoverOffset: 8,
        }]
      }
    })

    // ── Trek Status Bar ──
    const trekStatusData = computed(() => {
      if (!data.value) return { labels: [], datasets: [] }
      const dist = data.value.trek_status_distribution
      const colorMap = {
        Pending: PALETTE.amber, Approved: PALETTE.cyan,
        Open: PALETTE.green, Closed: PALETTE.red, Completed: PALETTE.blue
      }
      const labels = Object.keys(dist)
      return {
        labels,
        datasets: [{
          label: 'Treks',
          data: labels.map(l => dist[l]),
          backgroundColor: labels.map(l => (colorMap[l] || PALETTE.purple).replace(', 1)', ', 0.75)')),
          borderColor: labels.map(l => colorMap[l] || PALETTE.purple),
          borderWidth: 1,
          borderRadius: 8,
          borderSkipped: false,
        }]
      }
    })

    // ── Chart options ──
    const basePlugins = {
      legend: { position: 'top' },
      tooltip: {}
    }

    const lineOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { ...basePlugins, legend: { display: false } },
      scales: darkScales()
    }

    const barOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { ...basePlugins, legend: { display: false } },
      scales: darkScales()
    }

    const topTreksOptions = {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { ...basePlugins, legend: { display: false } },
      scales: darkScales({
        y: { ticks: { color: '#f8fafc', font: { weight: '500' } } }
      })
    }

    const trekStatusOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { ...basePlugins, legend: { display: false } },
      scales: darkScales()
    }

    const doughnutOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' },
        tooltip: {}
      },
      cutout: '62%',
    }

    onMounted(fetchAnalytics)

    return {
      loading, error,
      monthlyBookingsData, monthlyParticipationData, topTreksData,
      difficultyData, bookingStatusData, paymentData, trekStatusData,
      lineOptions, barOptions, topTreksOptions, doughnutOptions, trekStatusOptions,
    }
  }
}
</script>

<style scoped>
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.75rem;
  margin-bottom: 2rem;
}
.charts-row--3 {
  grid-template-columns: repeat(3, 1fr);
  margin-bottom: 2rem;
}

.chart-card {
  padding: 1.5rem;
}

.chart-header {
  margin-bottom: 1.25rem;
}
.chart-header h3 {
  margin: 0 0 0.2rem 0;
  font-size: 1rem;
  font-weight: 700;
}
.chart-sub {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.chart-body {
  height: 260px;
  position: relative;
}
.chart-body--tall {
  height: 340px;
}
.chart-body--sm {
  height: 220px;
}

@media (max-width: 1024px) {
  .charts-row--3 {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .charts-row,
  .charts-row--3 {
    grid-template-columns: 1fr;
  }
  .chart-body { height: 220px; }
  .chart-body--tall { height: 280px; }
  .chart-body--sm { height: 200px; }
}
</style>
