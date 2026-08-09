<template>
  <aside class="bg-dark text-light py-3" style="width: 250px; min-height: 100vh;">
    <div class="sidebar-header">
      <h2>Staff Portal</h2>
      <p class="subtitle">Trek Management</p>
    </div>
    <nav class="nav flex-column">
      <router-link to="/staff" class="nav-link d-flex align-items-center" active-class="active"><i class="fas fa-tachometer-alt me-2"></i>Dashboard</router-link>
      <router-link to="/staff/treks" class="nav-link d-flex align-items-center" active-class="active"><i class="fas fa-hiking me-2"></i>My Treks</router-link>
    </nav>
    <div class="sidebar-footer">
      <button @click="logout" class="btn btn-danger w-100">Logout</button>
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
