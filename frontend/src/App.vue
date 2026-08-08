<template>
  <ToastNotification />
  <ConfirmDialog />

  <nav class="tma-navbar navbar navbar-expand-lg" :class="{ scrolled }">
    <div class="container-fluid px-3 px-lg-4">
      <router-link class="navbar-brand tma-brand" :to="userDashboardRoute">
        <span class="nav-brand-icon"><i class="bi bi-signpost-split-fill"></i></span>
        <span class="nav-brand-text">
          <span class="nav-brand-name">TMA</span>
          <span class="nav-brand-tag">Trekking Management</span>
        </span>
      </router-link>

      <button class="navbar-toggler tma-toggler" type="button"
        @click="navOpen = !navOpen" aria-controls="navbarNav"
        :aria-expanded="navOpen" aria-label="Toggle navigation">
        <i :class="navOpen ? 'bi bi-x-lg' : 'bi bi-list'"></i>
      </button>

      <div class="collapse navbar-collapse" id="navbarNav" :class="{ show: navOpen }">
        <ul class="navbar-nav ms-auto align-items-lg-center gap-lg-2">
          <li class="nav-item" v-if="isAuthenticated">
            <router-link class="tma-nav-link" :to="userDashboardRoute" @click="navOpen=false">
              <i class="bi bi-speedometer2"></i> Dashboard
            </router-link>
          </li>
          <li class="nav-item" v-if="!isAuthenticated">
            <router-link class="tma-nav-link" to="/login" @click="navOpen=false">
              <i class="bi bi-box-arrow-in-right"></i> Sign In
            </router-link>
          </li>
          <li class="nav-item" v-if="!isAuthenticated">
            <router-link class="tma-nav-link tma-nav-cta" to="/register" @click="navOpen=false">
              <i class="bi bi-person-plus"></i> Get Started
            </router-link>
          </li>
          <li class="nav-item" v-if="isAuthenticated">
            <span class="tma-user-chip">
              <i class="bi bi-person-circle"></i> {{ currentUser?.username }}
            </span>
          </li>
          <li class="nav-item" v-if="isAuthenticated">
            <button class="tma-nav-link tma-nav-logout" @click="logout">
              <i class="bi bi-box-arrow-right"></i> Logout
            </button>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <div class="tma-app-body">
    <router-view />
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import ToastNotification from './components/ToastNotification.vue'
import ConfirmDialog from './components/ConfirmDialog.vue'
import { useToast } from './composables/useToast.js'
import './assets/dashboard-layout.css'

export default {
  name: 'App',
  components: { ToastNotification, ConfirmDialog },
  setup() {
    const router = useRouter()
    const { success } = useToast()
    const navOpen = ref(false)
    const scrolled = ref(false)
    const authState = ref({
      token: localStorage.getItem('tma_token'),
      user: localStorage.getItem('tma_user') ? JSON.parse(localStorage.getItem('tma_user')) : null
    })

    const syncAuth = () => {
      const token = localStorage.getItem('tma_token')
      const userStr = localStorage.getItem('tma_user')
      authState.value.token = token
      try {
        authState.value.user = userStr ? JSON.parse(userStr) : null
      } catch (e) {
        authState.value.user = null
      }
    }

    const isAuthenticated = computed(() => !!authState.value.token && !!authState.value.user)
    const currentUser = computed(() => authState.value.user)

    const userDashboardRoute = computed(() => {
      if (!isAuthenticated.value) return '/'
      const role = currentUser.value?.role
      if (role === 'Admin') return '/admin'
      if (role === 'Trek Staff') return '/staff'
      if (role === 'Trekker') return '/trekker'
      return '/'
    })

    const logout = () => {
      localStorage.removeItem('tma_token')
      localStorage.removeItem('tma_user')
      syncAuth()
      success('Logged out successfully.')
      router.push('/login')
    }

    const onScroll = () => { scrolled.value = window.scrollY > 8 }

    onMounted(() => {
      window.addEventListener('scroll', onScroll)
      window.addEventListener('storage', syncAuth)
    })
    onUnmounted(() => {
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('storage', syncAuth)
    })

    router.afterEach(() => {
      navOpen.value = false
      syncAuth()
    })

    return { navOpen, scrolled, isAuthenticated, currentUser, userDashboardRoute, logout }
  }
}
</script>

<style>
/* ── Global resets ── */
*, *::before, *::after { box-sizing: border-box; }
body {
  margin: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg);
  background-image:
    radial-gradient(ellipse 80% 50% at 10% 0%,  rgba(61,139,101,.12), transparent 55%),
    radial-gradient(ellipse 60% 45% at 90% 15%, rgba(63,143,160,.07), transparent 50%),
    radial-gradient(ellipse 50% 35% at 50% 100%,rgba(212,146,74,.05), transparent 45%);
  background-attachment: fixed;
  color: var(--text-1);
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}

/* ── Navbar ── */
.tma-navbar {
  position: fixed; top: 0; left: 0; right: 0;
  z-index: 1000;
  background: rgba(9,18,14,.82);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border);
  transition: background .3s, box-shadow .3s;
  height: var(--nav-h);
}
.tma-navbar.scrolled {
  background: rgba(9,18,14,.97);
  box-shadow: 0 4px 24px rgba(0,0,0,.35);
}

/* Brand */
.tma-brand { display:flex; align-items:center; gap:.7rem; text-decoration:none; }
.nav-brand-icon {
  width:36px; height:36px; display:flex; align-items:center; justify-content:center;
  background: var(--g-hero); border-radius: var(--r-s);
  color:#fff; font-size:1rem; box-shadow:0 3px 10px var(--green-glow); flex-shrink:0;
}
.nav-brand-text { display:flex; flex-direction:column; line-height:1.2; }
.nav-brand-name {
  font-weight:800; font-size:1.1rem; letter-spacing:-.03em;
  background:var(--g-brand); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
}
.nav-brand-tag { font-size:.62rem; font-weight:600; color:var(--text-3); text-transform:uppercase; letter-spacing:.08em; }

/* Toggler */
.tma-toggler {
  background:rgba(61,139,101,.08); border:1px solid var(--border); color:var(--text-1);
  border-radius:var(--r-s); padding:.4rem .6rem; font-size:1.1rem;
  display:flex; align-items:center; justify-content:center; transition:background .2s;
}
.tma-toggler:hover { background:rgba(61,139,101,.15); }
.tma-toggler:focus { outline:none; box-shadow:0 0 0 3px var(--green-glow); }

/* Nav links */
.tma-nav-link {
  color: var(--text-2) !important; font-weight:600; font-size:.875rem;
  padding:.48rem .95rem !important; border-radius:var(--r-s);
  border:none; background:none; cursor:pointer;
  transition:color .18s, background .18s; text-decoration:none;
  display:inline-flex; align-items:center; gap:.4rem;
}
.tma-nav-link:hover { color:var(--text-1) !important; background:rgba(61,139,101,.09); }
.tma-nav-link.router-link-active { color:var(--green-l) !important; }
.tma-nav-cta { background:var(--g-hero) !important; color:#fff !important; box-shadow:0 2px 10px var(--green-glow); }
.tma-nav-cta:hover { filter:brightness(1.1); color:#fff !important; transform:translateY(-1px); }
.tma-user-chip { color:var(--text-2); font-size:.875rem; font-weight:600; padding:.4rem .75rem; display:inline-flex; align-items:center; gap:.4rem; }
.tma-nav-logout { color:var(--err) !important; }
.tma-nav-logout:hover { background:var(--err-bg); color:#f0a090 !important; }

/* Mobile collapse */
@media (max-width:991px) {
  .navbar-collapse {
    background:rgba(9,18,14,.98); border-radius:var(--r-m);
    margin-top:.65rem; padding:.65rem; border:1px solid var(--border);
  }
  .navbar-nav { gap:.2rem !important; }
  .tma-nav-link { width:100%; }
  .nav-brand-tag { display:none; }
}

/* App body offset */
.tma-app-body { padding-top: var(--nav-h); }
.tma-app-body > .admin-layout { min-height: calc(100vh - var(--nav-h)); }
</style>
