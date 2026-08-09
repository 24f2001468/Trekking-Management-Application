<template>
  <div class="admin-layout">
    <div class="sidebar-backdrop" :class="{ 'is-visible': sidebarOpen }" @click="sidebarOpen = false"></div>
    <TrekkerSidebar :class="{ 'is-open': sidebarOpen }" />
    <main class="admin-content">
      <router-view :key="$route.fullPath" />
    </main>
    <button class="sidebar-toggle-btn" @click="sidebarOpen = !sidebarOpen" aria-label="Toggle sidebar">
      <span>{{ sidebarOpen ? "?" : "?" }}</span>
    </button>
  </div>
</template>

<script>
import { ref } from 'vue'
import TrekkerSidebar from '../components/trekker/TrekkerSidebar.vue'
export default {
  name: 'TrekkerDashboard',
  components: { TrekkerSidebar },
  setup() {
    const sidebarOpen = ref(false)
    return { sidebarOpen }
  }
}
</script>
