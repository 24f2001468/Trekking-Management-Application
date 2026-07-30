<template>
  <div class="admin-layout">
    <StaffSidebar />
    <main class="admin-content">
      <router-view />
    </main>
  </div>
</template>

<script>
import StaffSidebar from '../components/staff/StaffSidebar.vue'
import '../assets/dashboard-layout.css'

export default {
  name: 'StaffDashboard',
  components: {
    StaffSidebar
  }
}
</script>
