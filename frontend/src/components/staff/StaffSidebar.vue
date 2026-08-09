<template>
  <aside class="admin-sidebar sidebar--staff">
    <div class="sidebar-header">
      <h2>Staff Portal</h2>
      <p class="subtitle">Trek Management</p>
    </div>
    <nav class="sidebar-nav">
      <router-link to="/staff"       class="nav-item" exact-active-class="active"><i class="bi bi-speedometer2"></i> Dashboard</router-link>
      <router-link to="/staff/treks" class="nav-item" active-class="active"><i class="bi bi-map-fill"></i> My Treks</router-link>
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
  name: 'StaffSidebar',
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
