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
import '../assets/admin.css' // Import premium styles for admin section

export default {
  name: 'AdminDashboard',
  components: {
    AdminSidebar
  }
}
</script>
