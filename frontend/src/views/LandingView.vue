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

    <!-- ── Feature Cards ── -->
    <section class="section features-section">
      <div class="section-header">
        <h2>Everything You Need</h2>
        <p>A complete trekking platform for adventurers and organizers</p>
      </div>
      <div class="features-grid">
        <div class="feature-card glass-panel" v-for="f in features" :key="f.title">
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
import { computed } from 'vue'

export default {
  name: 'LandingView',
  setup() {
    const isAuthenticated = computed(() => !!localStorage.getItem('tma_token'))
    const userDashboardRoute = computed(() => {
      const u = localStorage.getItem('tma_user')
      if (!u) return '/'
      try {
        const role = JSON.parse(u).role
        if (role === 'Admin') return '/admin'
        if (role === 'Trek Staff') return '/staff'
        return '/trekker'
      } catch { return '/' }
    })

    const features = [
      { icon: '🗓️', title: 'Easy Booking', desc: 'Browse all available treks and book your spot in seconds with real-time slot tracking.' },
      { icon: '🛡️', title: 'Safe & Managed', desc: 'Dedicated trek staff monitor every trek from registration through completion.' },
      { icon: '📊', title: 'Live Analytics', desc: 'Admins get full visibility into participation, payments, and trends via rich charts.' },
      { icon: '📄', title: 'Export History', desc: 'Download your complete trekking history as a CSV with one click.' },
      { icon: '🔔', title: 'Reminders', desc: 'Automated daily reminders ensure no trekker misses their scheduled adventure.' },
      { icon: '💳', title: 'Payment Tracking', desc: 'Transparent payment status management for admins and trekkers alike.' },
    ]

    return { isAuthenticated, userDashboardRoute, features }
  }
}
</script>

<style scoped>
.landing-page { min-height: calc(100vh - 60px); padding-bottom: 4rem; }

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
  gap: .5rem;
  background: rgba(16,185,129,.12);
  border: 1px solid rgba(16,185,129,.3);
  color: #34d399;
  font-size: .8rem;
  font-weight: 600;
  padding: .35rem .9rem;
  border-radius: 9999px;
  margin-bottom: 1.5rem;
}

.hero-title {
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 800;
  line-height: 1.15;
  margin: 0 0 1.25rem 0;
}

.gradient-text {
  background: linear-gradient(135deg, #10b981, #06b6d4);
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

.hero-cta { display: flex; gap: 1rem; flex-wrap: wrap; }

.btn-outline {
  background: rgba(255,255,255,.07);
  border: 1px solid rgba(255,255,255,.18);
  color: var(--text-1);
}
.btn-outline:hover { background: rgba(255,255,255,.12); transform: translateY(-2px); }

.mountain-art { font-size: 8rem; animation: float 4s ease-in-out infinite; }
@keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-14px)} }

.section { max-width:1200px; margin:0 auto 4rem; padding:0 2rem; }
.section-header { text-align:center; margin-bottom:2.5rem; }
.section-header h2 { font-size:1.85rem; font-weight:700; margin:0 0 .5rem 0; }
.section-header p { color:var(--text-2); font-size:.95rem; margin:0; }

.features-section { margin-bottom: 4rem; }
.features-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:1.5rem; }
.feature-card { padding:2rem; transition:transform .3s ease; }
.feature-card:hover { transform:translateY(-6px); }
.feature-icon { font-size:2.2rem; margin-bottom:1rem; }
.feature-card h3 { font-size:1.05rem; font-weight:700; margin:0 0 .6rem 0; }
.feature-card p { color:var(--text-2); font-size:.875rem; line-height:1.6; margin:0; }

.cta-section { max-width:1200px; margin:0 auto 3rem; padding:3.5rem 2rem; text-align:center; }
.cta-section h2 { font-size:1.75rem; font-weight:700; margin:0 0 .75rem 0; }
.cta-section p { color:var(--text-2); margin:0 0 2rem 0; }
.cta-buttons { display:flex; justify-content:center; gap:1rem; flex-wrap:wrap; }

.landing-footer { text-align:center; color:var(--text-2); font-size:.8rem; padding:1.5rem; border-top:1px solid var(--border); }

@media (max-width: 768px) {
  .hero-section { grid-template-columns:1fr; padding:3rem 1.5rem 2rem; text-align:center; }
  .hero-cta { justify-content:center; }
  .hero-graphic { display:none; }
  .section { padding:0 1rem; }
  .features-grid { grid-template-columns:1fr; }
}
</style>
