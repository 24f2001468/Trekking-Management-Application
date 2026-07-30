<template>
  <aside class="admin-sidebar">
    <div class="sidebar-header">
      <h2>Trekker Portal</h2>
      <p class="subtitle">Explore & Book</p>
    </div>
    
    <nav class="sidebar-nav">
      <router-link to="/trekker" class="nav-item" exact-active-class="active">
        <i class="icon">🏠</i> Home
      </router-link>
      <router-link to="/trekker/browse" class="nav-item" active-class="active">
        <i class="icon">🔍</i> Browse Treks
      </router-link>
      <router-link to="/trekker/bookings" class="nav-item" active-class="active">
        <i class="icon">📅</i> My Bookings
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <button @click="logout" class="btn-premium btn-danger" style="width: 100%;">
        🚪 Logout
      </button>
    </div>
  </aside>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'TrekkerSidebar',
  setup() {
    const router = useRouter()

    const logout = () => {
      localStorage.removeItem('tma_token')
      localStorage.removeItem('tma_user')
      router.push('/login')
    }

    return { logout }
  }
}
</script>

<style scoped>
.sidebar-header {
  padding: 2rem 1.5rem;
  border-bottom: var(--glass-border);
}
.sidebar-header h2 {
  margin: 0;
  font-size: 1.5rem;
  background: linear-gradient(to right, #60a5fa, #34d399);
  -webkit-background-clip: text;
  color: transparent;
}
.subtitle {
  margin: 0.25rem 0 0 0;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.sidebar-nav {
  padding: 1.5rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 0.875rem 1rem;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.2s ease;
  font-weight: 500;
}

.nav-item .icon {
  margin-right: 0.75rem;
  font-size: 1.2rem;
  font-style: normal;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
  transform: translateX(5px);
}

.nav-item.active {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border-left: 3px solid #10b981;
}

.sidebar-footer {
  padding: 1.5rem;
  border-top: var(--glass-border);
}
</style>
