<template>
  <aside class="admin-sidebar sidebar--trekker">
    <div class="sidebar-header">
      <h2>Trekker Portal</h2>
      <p class="subtitle">Explore &amp; Book</p>
    </div>
    <nav class="sidebar-nav">
      <router-link to="/trekker"           class="nav-item" exact-active-class="active"><i class="bi bi-house-fill"></i> Home</router-link>
      <router-link to="/trekker/browse"    class="nav-item" active-class="active"><i class="bi bi-compass-fill"></i> Browse Treks</router-link>
      <router-link to="/trekker/bookings"  class="nav-item" active-class="active"><i class="bi bi-calendar-check-fill"></i> My Bookings</router-link>
      <router-link to="/trekker/history"   class="nav-item" active-class="active"><i class="bi bi-clock-history"></i> Trek History</router-link>
      <router-link to="/trekker/profile"   class="nav-item" active-class="active"><i class="bi bi-person-fill"></i> My Profile</router-link>
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
  name: 'TrekkerSidebar',
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
