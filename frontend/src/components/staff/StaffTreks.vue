<template>
  <div>
    <div class="page-header">
      <h1>My Assigned Treks</h1>
    </div>

    <div v-if="loading" class="loading">Loading treks...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else class="premium-table-wrapper">
      <table class="premium-table">
        <thead>
          <tr>
            <th>Trek Name</th>
            <th>Location</th>
            <th>Dates</th>
            <th>Status</th>
            <th>Registered</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in treks" :key="t.id">
            <td><strong>{{ t.name }}</strong></td>
            <td>{{ t.location }}</td>
            <td style="font-size: 0.85rem;">{{ t.start_date }} <br>to<br> {{ t.end_date }}</td>
            <td>
              <span class="badge" 
                :class="{
                  'badge-success': t.status === 'Open',
                  'badge-warning': t.status === 'Ongoing' || t.status === 'Pending',
                  'badge-danger': t.status === 'Closed',
                  'badge-primary': t.status === 'Completed'
                }">
                {{ t.status }}
              </span>
            </td>
            <td>{{ t.participants_count }} ({{ t.available_slots }} left)</td>
            <td>
              <router-link :to="`/staff/treks/${t.id}`" class="btn-premium btn-primary" style="padding: 0.4rem 0.8rem; font-size: 0.85rem; text-decoration: none;">
                Manage
              </router-link>
            </td>
          </tr>
          <tr v-if="treks.length === 0">
            <td colspan="6" style="text-align: center; padding: 2rem;">No treks assigned.</td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'StaffTreks',
  setup() {
    const treks = ref([])
    const loading = ref(true)
    const error = ref('')

    const fetchTreks = async () => {
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch('/api/staff/treks', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (!response.ok) throw new Error('Failed to load treks')
        treks.value = await response.json()
      } catch (err) {
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    onMounted(fetchTreks)

    return { treks, loading, error }
  }
}
</script>
