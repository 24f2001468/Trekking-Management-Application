<template>
  <aside class="admin-sidebar">
    <div class="sidebar-header">
      <h2>TMA Admin</h2>
      <p class="subtitle">Management Console</p>
    </div>
    <nav class="sidebar-nav">
      <router-link to="/admin"             class="nav-item" exact-active-class="active">Dashboard</router-link>
      <router-link to="/admin/treks"       class="nav-item" active-class="active">Treks</router-link>
      <router-link to="/admin/users"       class="nav-item" active-class="active">Users</router-link>
      <router-link to="/admin/staff"       class="nav-item" active-class="active">Staff</router-link>
      <router-link to="/admin/bookings"    class="nav-item" active-class="active">Bookings</router-link>
      <router-link to="/admin/payments"    class="nav-item" active-class="active">Payments</router-link>
      <router-link to="/admin/trek-search" class="nav-item" active-class="active">Trek Search</router-link>
      <router-link to="/admin/analytics"   class="nav-item" active-class="active">Analytics</router-link>
    </nav>
    <div class="sidebar-footer">
      <button @click="logout" class="btn-premium btn-danger" style="width:100%;">Logout</button>
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
