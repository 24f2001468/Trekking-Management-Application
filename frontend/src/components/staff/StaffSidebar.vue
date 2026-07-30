<template>
  <aside class="admin-sidebar">
    <div class="sidebar-header">
      <h2>Staff Portal</h2>
      <p class="subtitle">Trek Management</p>
    </div>
    
    <nav class="sidebar-nav">
      <router-link to="/staff" class="nav-item" exact-active-class="active">
        <i class="icon">📊</i> Dashboard
      </router-link>
      <router-link to="/staff/treks" class="nav-item" active-class="active">
        <i class="icon">🏔️</i> My Treks
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
  name: 'StaffSidebar',
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
  background: linear-gradient(to right, #f59e0b, #10b981);
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
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
  border-left: 3px solid #f59e0b;
}

.sidebar-footer {
  padding: 1.5rem;
  border-top: var(--glass-border);
}
</style>
