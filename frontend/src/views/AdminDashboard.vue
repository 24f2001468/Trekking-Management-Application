<template>
  <div class="admin-layout">
    <div class="sidebar-backdrop" :class="{ 'is-visible': sidebarOpen }" @click="sidebarOpen = false"></div>
    <AdminSidebar :class="{ 'is-open': sidebarOpen }" />
    <main class="admin-content">
      <router-view />
    </main>
    <button class="sidebar-toggle-btn" @click="sidebarOpen = !sidebarOpen" aria-label="Toggle sidebar">
      <i :class="sidebarOpen ? 'bi bi-x-lg' : 'bi bi-layout-sidebar'"></i>
    </button>
  </div>
</template>

<script>
import { ref } from 'vue'
import AdminSidebar from '../components/admin/AdminSidebar.vue'
export default {
  name: 'AdminDashboard',
  components: { AdminSidebar },
  setup() {
    const sidebarOpen = ref(false)
    return { sidebarOpen }
  }
}
</script>
