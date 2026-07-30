<template>
  <div class="admin-layout">
    <TrekkerSidebar />
    <main class="admin-content">
      <router-view />
    </main>
  </div>
</template>

<script>
import TrekkerSidebar from '../components/trekker/TrekkerSidebar.vue'
import '../assets/dashboard-layout.css'

export default {
  name: 'TrekkerDashboard',
  components: {
    TrekkerSidebar
  }
}
</script>
