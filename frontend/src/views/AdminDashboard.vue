<template>
  <div class="admin-layout">
    <AdminSidebar />
    <main class="admin-content">
      <router-view />
    </main>
  </div>
</template>

<script>
import AdminSidebar from '../components/admin/AdminSidebar.vue'
import '../assets/dashboard-layout.css' // Import premium styles for dashboard layout

export default {
  name: 'AdminDashboard',
  components: {
    AdminSidebar
  }
}
</script>
