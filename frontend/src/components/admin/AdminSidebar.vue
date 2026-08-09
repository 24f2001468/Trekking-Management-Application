<template>
  <aside class="admin-sidebar">
    <div class="sidebar-header">
      <h2>TMA Admin</h2>
      <p class="subtitle">Management Console</p>
    </div>
    <nav class="sidebar-nav">
      <router-link to="/admin"             class="nav-item" exact-active-class="active"><i class="bi bi-speedometer2"></i> Dashboard</router-link>
      <router-link to="/admin/treks"       class="nav-item" active-class="active"><i class="bi bi-map-fill"></i> Treks</router-link>
      <router-link to="/admin/users"       class="nav-item" active-class="active"><i class="bi bi-people-fill"></i> Users</router-link>
      <router-link to="/admin/staff"       class="nav-item" active-class="active"><i class="bi bi-person-badge-fill"></i> Staff</router-link>
      <router-link to="/admin/bookings"    class="nav-item" active-class="active"><i class="bi bi-calendar-check-fill"></i> Bookings</router-link>
      <router-link to="/admin/payments"    class="nav-item" active-class="active"><i class="bi bi-credit-card-fill"></i> Payments</router-link>
      <router-link to="/admin/trek-search" class="nav-item" active-class="active"><i class="bi bi-search"></i> Trek Search</router-link>
      <router-link to="/admin/analytics"   class="nav-item" active-class="active"><i class="bi bi-bar-chart-fill"></i> Analytics</router-link>
    </nav>
    <div class="sidebar-footer">
      <button @click="logout" class="btn btn-danger w-100">
        <i class="bi bi-box-arrow-right"></i> Logout
      </button>
    </div>
  </aside>
</template>
<script>
import { useRouter } from 'vue-router'
import { useToast } from '../../composables/useToast.js'
export default {
  name: 'AdminSidebar',
  setup() {
    const router = useRouter()
    const { success } = useToast()
    const logout = () => {
      localStorage.removeItem('tma_token')
      localStorage.removeItem('tma_user')
      success('Logged out.')
      router.push('/login')
    }
    return { logout }
  }
}
</script>
