<template>
  <ToastNotification />
  <ConfirmDialog />

  <nav class="navbar navbar-expand-lg bg-dark navbar-dark sticky-top" :class="{ scrolled }">
    <div class="container-fluid py-2 px-3 px-lg-4">
      <router-link class="navbar-brand" :to="userDashboardRoute">
        <span class="nav-brand-icon"><i class="fas fa-mountain"></i></span>
        <span class="nav-brand-text">
          <span class="nav-brand-name">TMA</span>
          <span class="nav-brand-tag">Trekking Management</span>
        </span>
      </router-link>

      <button class="navbar-toggler tma-toggler" type="button"
        @click="navOpen = !navOpen" aria-controls="navbarNav"
        :aria-expanded="navOpen" aria-label="Toggle navigation">
        <span>{{ navOpen ? '✕' : '☰' }}</span>
      </button>

      <div class="collapse navbar-collapse" id="navbarNav" :class="{ show: navOpen }">
        <ul class="navbar-nav ms-auto align-items-lg-center gap-lg-2">
          <li class="nav-item" v-if="isAuthenticated">
            <router-link class="nav-link" :to="userDashboardRoute" @click="navOpen=false">
              <span>📊</span> Dashboard
            </router-link>
          </li>
          <li class="nav-item" v-if="!isAuthenticated">
            <router-link class="nav-link" to="/login" @click="navOpen=false">
              <span>→</span> Sign In
            </router-link>
          </li>
          <li class="nav-item" v-if="!isAuthenticated">
            <router-link class="btn btn-primary nav-link" to="/register" @click="navOpen=false">
              <span>➕</span> Get Started
            </router-link>
          </li>
          <li class="nav-item" v-if="isAuthenticated">
            <span class="badge bg-secondary">
              <span>👤</span> {{ currentUser?.username }}
            </span>
          </li>
          <li class="nav-item" v-if="isAuthenticated">
            <button class="nav-link btn btn-outline-light" @click="logout">
              <span>🚪</span> Logout
            </button>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <div class="container-fluid">
    <router-view />
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import ToastNotification from './components/ToastNotification.vue'
import ConfirmDialog from './components/ConfirmDialog.vue'
import { useToast } from './composables/useToast.js'
// import './assets/dashboard-layout.css' // removed per Bootstrap‑only styling plan

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
