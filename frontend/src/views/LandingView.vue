<template>
  <div class="landing-page">

    <!-- ── Hero ── -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-badge">🏔️ Trekking Management Application</div>
        <h1 class="hero-title">
          Discover Your Next
          <span class="gradient-text">Adventure</span>
        </h1>
        <p class="hero-subtitle">
          Join thousands of trekkers exploring breathtaking trails.
          Browse, book, and track your trekking journey — all in one place.
        </p>
        <div class="hero-cta">
          <router-link v-if="!isAuthenticated" to="/register" class="btn-premium btn-primary btn-lg">
            Get Started Free
          </router-link>
          <router-link v-if="!isAuthenticated" to="/login" class="btn-premium btn-outline btn-lg">
            Sign In
          </router-link>
          <router-link v-if="isAuthenticated" :to="userDashboardRoute" class="btn-premium btn-primary btn-lg">
            Go to My Dashboard
          </router-link>
        </div>
      </div>
      <div class="hero-graphic" aria-hidden="true">
        <div class="mountain-art">🏔️</div>
      </div>
    </section>

    <!-- ── Live Stats Strip ── -->
    <section class="stats-strip" v-if="!statsLoading">
      <div class="strip-stat" v-for="s in heroStats" :key="s.label">
        <span class="strip-val">{{ s.value }}</span>
        <span class="strip-label">{{ s.label }}</span>
      </div>
    </section>

    <!-- ── Charts Section ── -->
    <section class="section">
      <div class="section-header">
        <h2>Platform Insights</h2>
        <p>Live trekking statistics — updated every 5 minutes</p>
      </div>

      <div v-if="statsLoading" class="loading">Loading statistics...</div>
      <div v-else-if="statsError" class="error">{{ statsError }}</div>

      <div v-else class="charts-grid">

        <!-- Top Treks Bar -->
        <div class="chart-card glass-panel">
          <div class="chart-header">
            <h3>🏆 Most Popular Treks</h3>
            <span class="chart-sub">By booking count</span>
          </div>
          <div class="chart-body" v-if="topTreksData.labels.length > 0">
            <Bar :data="topTreksData" :options="barOptions" />
          </div>
          <div class="empty-chart" v-else>No bookings yet — be the first!</div>
        </div>

        <!-- Difficulty Doughnut -->
        <div class="chart-card glass-panel">
          <div class="chart-header">
            <h3>⛰️ Trek Difficulty Mix</h3>
            <span class="chart-sub">Across all available treks</span>
          </div>
          <div class="chart-body chart-body--sm" v-if="difficultyLabels.length > 0">
            <Doughnut :data="difficultyData" :options="doughnutOptions" />
          </div>
          <div class="empty-chart" v-else>No treks published yet.</div>
        </div>

        <!-- Status Doughnut -->
        <div class="chart-card glass-panel">
          <div class="chart-header">
            <h3>📋 Trek Status</h3>
            <span class="chart-sub">Open, completed, and upcoming</span>
          </div>
          <div class="chart-body chart-body--sm" v-if="statusLabels.length > 0">
            <Doughnut :data="statusData" :options="doughnutOptions" />
          </div>
          <div class="empty-chart" v-else>No treks yet.</div>
        </div>

      </div>
    </section>

    <!-- ── Feature Cards ── -->
    <section class="section features-section">
      <div class="section-header">
        <h2>Everything You Need</h2>
        <p>A complete trekking platform for adventurers and organizers</p>
      </div>
      <div class="features-grid">
        <div class="feature-card glass-panel" v-for="f in features" :key="f.icon">
          <div class="feature-icon">{{ f.icon }}</div>
          <h3>{{ f.title }}</h3>
          <p>{{ f.desc }}</p>
        </div>
      </div>
    </section>

    <!-- ── CTA Banner ── -->
    <section class="cta-section glass-panel">
      <h2>Ready for your next adventure?</h2>
      <p>Create a free Trekker account and start exploring today.</p>
      <div class="cta-buttons">
        <router-link v-if="!isAuthenticated" to="/register" class="btn-premium btn-primary btn-lg">
          Create Free Account
        </router-link>
        <router-link v-if="!isAuthenticated" to="/login" class="btn-premium btn-outline btn-lg">
          Already a member? Sign In
        </router-link>
        <router-link v-if="isAuthenticated" :to="userDashboardRoute" class="btn-premium btn-primary btn-lg">
          Go to My Dashboard
        </router-link>
      </div>
    </section>

    <!-- ── Footer ── -->
    <footer class="landing-footer">
      <span>© 2026 Trekking Management Application</span>
    </footer>

  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { Bar, Doughnut } from 'vue-chartjs'
import { PALETTE, PIE_COLORS, darkScales } from '../composables/useChartDefaults.js'

export default {
  name: 'LandingView',
  components: { Bar, Doughnut },
  setup() {
    const stats = ref(null)
    const statsLoading = ref(true)
    const statsError = ref('')

    const fetchStats = async () => {
      try {
        const res = await fetch('http://localhost:5000/api/analytics/public/stats')
        if (!res.ok) throw new Error('Could not load stats')
        stats.value = await res.json()
      } catch (err) {
        statsError.value = err.message
      } finally {
        statsLoading.value = false
      }
    }

    // Strip hero stats
    const heroStats = computed(() => {
      if (!stats.value) return []
      return [
        { value: stats.value.total_treks, label: 'Total Treks' },
        { value: stats.value.open_treks, label: 'Open for Booking' },
        { value: stats.value.total_trekkers, label: 'Active Trekkers' },
        { value: stats.value.total_bookings, label: 'Adventures Booked' },
        { value: stats.value.completed_treks, label: 'Treks Completed' },
      ]
    })

    // Top treks bar chart
    const topTreksData = computed(() => {
      if (!stats.value || !stats.value.top_treks.length) return { labels: [], datasets: [] }
      return {
        labels: stats.value.top_treks.map(t => t.name),
        datasets: [{
          label: 'Bookings',
          data: stats.value.top_treks.map(t => t.bookings),
          backgroundColor: stats.value.top_treks.map((_, i) =>
            PIE_COLORS[i % PIE_COLORS.length].replace(', 1)', ', 0.72)')
          ),
          borderColor: stats.value.top_treks.map((_, i) => PIE_COLORS[i % PIE_COLORS.length]),
          borderWidth: 1,
          borderRadius: 6,
          borderSkipped: false,
        }]
      }
    })

    // Difficulty doughnut
    const difficultyLabels = computed(() =>
      stats.value ? Object.keys(stats.value.difficulty_breakdown) : []
    )
    const difficultyData = computed(() => {
      if (!stats.value) return { labels: [], datasets: [] }
      const dist = stats.value.difficulty_breakdown
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

    // Status doughnut
    const statusLabels = computed(() =>
      stats.value ? Object.keys(stats.value.status_breakdown) : []
    )
    const statusData = computed(() => {
      if (!stats.value) return { labels: [], datasets: [] }
      const dist = stats.value.status_breakdown
      const colorMap = {
        Pending: PALETTE.amber, Approved: PALETTE.cyan,
        Open: PALETTE.green, Closed: PALETTE.red, Completed: PALETTE.blue
      }
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

    // Chart options
    const barOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: darkScales()
    }

    const doughnutOptions = {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '60%',
      plugins: { legend: { position: 'bottom' } }
    }

    const features = [
      { icon: '🗓️', title: 'Easy Booking', desc: 'Browse all available treks and book your spot in seconds with real-time slot tracking.' },
      { icon: '🛡️', title: 'Safe & Managed', desc: 'Dedicated trek staff monitor every trek from registration through completion.' },
      { icon: '📊', title: 'Live Analytics', desc: 'Admins get full visibility into participation, payments, and trends via rich charts.' },
      { icon: '📄', title: 'Export History', desc: 'Download your complete trekking history as a CSV with one click.' },
      { icon: '🔔', title: 'Reminders', desc: 'Automated daily reminders ensure no trekker misses their scheduled adventure.' },
      { icon: '💳', title: 'Payment Tracking', desc: 'Transparent payment status management for admins and trekkers alike.' },
    ]

    const isAuthenticated = computed(() => !!localStorage.getItem('tma_token'))
    const userDashboardRoute = computed(() => {
      if (!isAuthenticated.value) return '/'
      const u = localStorage.getItem('tma_user')
      let user = null
      if (u) { try { user = JSON.parse(u) } catch(e) {} }
      const role = user?.role
      if (role === 'Admin') return '/admin'
      if (role === 'Trek Staff') return '/staff'
      if (role === 'Trekker') return '/trekker'
      return '/'
    })

    return {
      stats, statsLoading, statsError, heroStats,
      topTreksData, difficultyData, difficultyLabels, statusData, statusLabels,
      barOptions, doughnutOptions,
      features, isAuthenticated, userDashboardRoute
    }
  }
}
</script>

<style scoped>
.landing-page {
  min-height: calc(100vh - 64px);
  padding-bottom: 4rem;
}

/* ── Hero ── */
.hero-section {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: 3rem;
  padding: 5rem 3rem 4rem;
  max-width: 1200px;
  margin: 0 auto;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(59,130,246,0.15);
  border: 1px solid rgba(59,130,246,0.35);
  color: #93c5fd;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.35rem 0.9rem;
  border-radius: 9999px;
  margin-bottom: 1.5rem;
  letter-spacing: 0.03em;
}

.hero-title {
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 800;
  line-height: 1.15;
  margin: 0 0 1.25rem 0;
}

.gradient-text {
  background: linear-gradient(135deg, #34d399, #38bdf8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  color: var(--text-2);
  font-size: 1.1rem;
  line-height: 1.7;
  max-width: 520px;
  margin: 0 0 2.5rem 0;
}

.hero-cta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-lg {
  padding: 0.9rem 2rem;
  font-size: 1rem;
}

.btn-outline {
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border-2);
  color: var(--text-1);
}
.btn-outline:hover {
  background: rgba(255,255,255,0.12);
  transform: translateY(-2px);
}

.hero-graphic {
  display: flex;
  align-items: center;
  justify-content: center;
}
.mountain-art {
  font-size: 9rem;
  filter: drop-shadow(0 0 40px rgba(16,185,129,0.3));
  animation: float 4s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-14px); }
}

/* ── Stats Strip ── */
.stats-strip {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0;
  margin: 0 2rem 3.5rem;
  border-radius: 16px;
  background: var(--card-solid);
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  overflow: hidden;
}

.strip-stat {
  flex: 1;
  min-width: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.75rem 1rem;
  border-right: 1px solid var(--border);
  transition: background 0.2s;
}
.strip-stat:last-child { border-right: none; }
.strip-stat:hover { background: rgba(255,255,255,0.03); }

.strip-val {
  font-size: 2.2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #34d399, #38bdf8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
}
.strip-label {
  font-size: 0.75rem;
  color: var(--text-2);
  font-weight: 600;
  margin-top: 0.4rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

/* ── Section ── */
.section {
  max-width: 1200px;
  margin: 0 auto 4rem;
  padding: 0 2rem;
}

.section-header {
  text-align: center;
  margin-bottom: 2.5rem;
}
.section-header h2 {
  font-size: 1.85rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}
.section-header p {
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin: 0;
}

/* ── Charts Grid ── */
.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 1.75rem;
}

.chart-card {
  padding: 1.5rem;
}
.chart-header { margin-bottom: 1.25rem; }
.chart-header h3 {
  margin: 0 0 0.2rem 0;
  font-size: 1rem;
  font-weight: 700;
}
.chart-sub {
  font-size: 0.78rem;
  color: var(--text-secondary);
}
.chart-body {
  height: 260px;
  position: relative;
}
.chart-body--sm { height: 200px; }
.empty-chart {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

/* ── Features ── */
.features-section {
  margin-bottom: 4rem;
}
.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}
.feature-card {
  padding: 2rem;
  transition: transform 0.3s ease;
}
.feature-card:hover { transform: translateY(-6px); }
.feature-icon {
  font-size: 2.2rem;
  margin-bottom: 1rem;
}
.feature-card h3 {
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0 0 0.6rem 0;
}
.feature-card p {
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.6;
  margin: 0;
}

/* ── CTA Banner ── */
.cta-section {
  max-width: 1200px;
  margin: 0 auto 3rem;
  padding: 3.5rem 2rem;
  text-align: center;
}
.cta-section h2 {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0 0 0.75rem 0;
}
.cta-section p {
  color: var(--text-secondary);
  margin: 0 0 2rem 0;
}
.cta-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

/* ── Footer ── */
.landing-footer {
  text-align: center;
  color: var(--text-secondary);
  font-size: 0.8rem;
  padding: 1.5rem;
  border-top: 1px solid rgba(255,255,255,0.06);
}

/* ── Responsive ── */
@media (max-width: 1024px) {
  .charts-grid { grid-template-columns: 1fr 1fr; }
  .charts-grid > :first-child { grid-column: 1 / -1; }
}

@media (max-width: 768px) {
  .hero-section {
    grid-template-columns: 1fr;
    padding: 3rem 1.5rem 2rem;
    text-align: center;
  }
  .hero-cta { justify-content: center; }
  .hero-graphic { display: none; }
  .stats-strip { margin: 0 1rem 2.5rem; }
  .section { padding: 0 1rem; }
  .charts-grid, .features-grid { grid-template-columns: 1fr; }
  .charts-grid > :first-child { grid-column: 1; }
}

@media (max-width: 480px) {
  .strip-stat { padding: 1.25rem 0.75rem; }
  .strip-val { font-size: 1.6rem; }
}
</style>
