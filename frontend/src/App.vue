<template>
  <ToastNotification />
  <ConfirmDialog />

  <nav class="navbar navbar-expand-lg navbar-dark sticky-top tma-navbar">
    <div class="container-fluid px-3 px-lg-4">

      <router-link class="navbar-brand d-flex align-items-center gap-2" :to="userDashboardRoute">
        <span>
          <span class="tma-brand-name">TMA</span>
          <span class="tma-brand-tag d-none d-md-block">Trekking Management</span>
        </span>
      </router-link>

      <button class="navbar-toggler border-0" type="button"
        @click="navOpen = !navOpen" :aria-expanded="navOpen" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" :class="{ show: navOpen }">
        <ul class="navbar-nav ms-auto align-items-lg-center gap-1">

          <li class="nav-item" v-if="isAuthenticated">
            <router-link class="nav-link px-3" :to="userDashboardRoute" @click="navOpen=false">
              <i class="bi bi-speedometer2"></i> Dashboard
            </router-link>
          </li>

          <li class="nav-item" v-if="!isAuthenticated">
            <router-link class="nav-link px-3" to="/login" @click="navOpen=false">
              <i class="bi bi-box-arrow-in-right"></i> Sign In
            </router-link>
          </li>

          <li class="nav-item" v-if="!isAuthenticated">
            <router-link class="btn btn-success px-3 py-2 ms-lg-2" to="/register" @click="navOpen=false">
              <i class="bi bi-person-plus"></i> Get Started
            </router-link>
          </li>

          <li class="nav-item" v-if="isAuthenticated">
            <span class="nav-link px-3 text-light opacity-75">
              <i class="bi bi-person-circle"></i> {{ currentUser?.username }}
            </span>
          </li>

          <li class="nav-item" v-if="isAuthenticated">
            <button class="btn btn-outline-danger btn-sm ms-lg-2 px-3" @click="logout">
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
      user: (() => { try { return JSON.parse(localStorage.getItem('tma_user') || 'null') } catch { return null } })()
    })

    const syncAuth = () => {
      authState.value.token = localStorage.getItem('tma_token')
      try { authState.value.user = JSON.parse(localStorage.getItem('tma_user') || 'null') }
      catch (e) { authState.value.user = null }
    }

    const isAuthenticated = computed(() => !!authState.value.token && !!authState.value.user)
    const currentUser = computed(() => authState.value.user)
    const userDashboardRoute = computed(() => {
      if (!isAuthenticated.value) return '/'
      const role = currentUser.value?.role
      if (role === 'Admin') return '/admin'
      if (role === 'Trek Staff') return '/staff'
      return '/trekker'
    })

    const logout = () => {
      localStorage.removeItem('tma_token')
      localStorage.removeItem('tma_user')
      syncAuth()
      success('Logged out successfully.')
      router.replace('/login')
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
    router.afterEach(() => { navOpen.value = false; syncAuth() })

    return { navOpen, scrolled, isAuthenticated, currentUser, userDashboardRoute, logout }
  }
}
</script>

<style>
.tma-navbar {
  background: #0f172a !important;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  min-height: 60px;
}
.tma-logo-icon {
  font-size: 1.5rem;
  color: #34d399;
}
.tma-brand-name {
  font-weight: 800;
  font-size: 1.1rem;
  letter-spacing: -0.02em;
  color: #34d399;
  display: block;
  line-height: 1.2;
}
.tma-brand-tag {
  font-size: 0.6rem;
  font-weight: 500;
  color: rgba(255,255,255,0.4);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.tma-navbar .nav-link {
  color: rgba(255,255,255,0.8) !important;
  font-weight: 500;
  font-size: 0.9rem;
  border-radius: 6px;
  transition: background 0.15s, color 0.15s;
}
.tma-navbar .nav-link:hover {
  color: #fff !important;
  background: rgba(255,255,255,0.08);
}
.tma-navbar .nav-link.router-link-active {
  color: #34d399 !important;
}
@media (max-width: 991px) {
  .navbar-collapse.show {
    background: #0f172a;
    padding: 0.75rem;
    border-radius: 8px;
    margin-top: 0.5rem;
    border: 1px solid rgba(255,255,255,0.1);
  }
}
.tma-app-body { padding-top: 60px; }
.tma-app-body > .admin-layout { min-height: calc(100vh - 60px); }
</style>
