<template>
  <div>
    <div class="page-header">
      <div>
        <router-link to="/staff/treks" style="color: var(--accent-color); text-decoration: none;">← Back to Treks</router-link>
        <h1 style="margin-top: 0.5rem;">Manage Trek: {{ trek?.name }}</h1>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading details...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else>
      <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 2rem;">
        
        <!-- Trek Details Form -->
        <div class="glass-panel" style="padding: 2rem;">
          <h2 style="margin-top: 0;">Trek Settings</h2>
          <form @submit.prevent="updateTrek">
            <div class="form-group">
              <label>Status</label>
              <select v-model="form.status" class="premium-input">
                <option value="Pending">Pending</option>
                <option value="Approved">Approved</option>
                <option value="Open">Open</option>
                <option value="Closed">Closed</option>
                <option value="Completed">Completed</option>
              </select>
            </div>
            <div class="form-group">
              <label>Available Slots</label>
              <input type="number" v-model="form.available_slots" class="premium-input" min="0">
            </div>
            
            <button type="submit" class="btn-premium btn-primary" style="width: 100%; margin-top: 1rem;" :disabled="submittingTrek">
              {{ submittingTrek ? 'Updating...' : 'Update Trek' }}
            </button>
          </form>
        </div>

        <!-- Participant List -->
        <div class="glass-panel" style="padding: 2rem;">
          <h2 style="margin-top: 0; display: flex; justify-content: space-between; align-items: center;">
            Participants
            <span class="badge badge-primary">{{ participants.length }} Registered</span>
          </h2>

          <div class="premium-table-wrapper" style="margin-top: 1.5rem;">
            <table class="premium-table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Booking Date</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in participants" :key="p.id">
                  <td>
                    <strong>{{ p.user?.username }}</strong><br>
                    <small style="color: var(--text-secondary)">{{ p.user?.email }}</small>
                  </td>
                  <td>{{ formatDate(p.booking_date) }}</td>
                  <td>
                    <span class="badge" 
                      :class="{
                        'badge-primary': p.status === 'Booked',
                        'badge-success': p.status === 'Completed',
                        'badge-danger': p.status === 'Cancelled'
                      }">
                      {{ p.status }}
                    </span>
                  </td>
                  <td>
                    <select v-model="p.newStatus" @change="updateParticipantStatus(p)" class="premium-input" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">
                      <option value="Booked">Booked</option>
                      <option value="Completed">Completed</option>
                      <option value="Cancelled">Cancelled</option>
                    </select>
                  </td>
                </tr>
                <tr v-if="participants.length === 0">
                  <td colspan="4" style="text-align: center; padding: 2rem;">No participants yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '../../composables/useToast.js'

export default {
  name: 'StaffTrekDetails',
  setup() {
    const route = useRoute()
    const trekId = route.params.id
    const { success, error: toastError } = useToast()
    
    const trek = ref(null)
    const participants = ref([])
    const loading = ref(true)
    const error = ref('')
    
    const form = ref({ status: '', available_slots: 0 })
    const submittingTrek = ref(false)

    const fetchTrek = async () => {
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch(`/api/staff/treks/${trekId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (!response.ok) throw new Error('Failed to load trek details')
        const data = await response.json()
        trek.value = data
        form.value = { status: data.status, available_slots: data.available_slots }
      } catch (err) {
        error.value = err.message
      }
    }

    const fetchParticipants = async () => {
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch(`/api/staff/treks/${trekId}/participants`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (response.ok) {
          const data = await response.json()
          participants.value = data.map(p => ({ ...p, newStatus: p.status }))
        }
      } catch (err) {
        console.error("Error fetching participants", err)
      }
    }

    const updateTrek = async () => {
      submittingTrek.value = true
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch(`/api/staff/treks/${trekId}`, {
          method: 'PUT',
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(form.value)
        })
        if (!response.ok) throw new Error('Failed to update trek')
        const data = await response.json()
        trek.value = data
        success('Trek settings updated successfully!')
      } catch (err) {
        toastError(err.message)
      } finally {
        submittingTrek.value = false
      }
    }

    const updateParticipantStatus = async (participant) => {
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch(`/api/staff/bookings/${participant.id}/status`, {
          method: 'PUT',
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ status: participant.newStatus })
        })
        if (!response.ok) {
          participant.newStatus = participant.status // revert
          throw new Error('Failed to update participant status')
        }
        const data = await response.json()
        participant.status = data.status
        success(`Participant status updated to "${data.status}".`)
      } catch (err) {
        toastError(err.message)
      }
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      const d = new Date(dateStr)
      return d.toLocaleDateString()
    }

    onMounted(async () => {
      await fetchTrek()
      if (trek.value) await fetchParticipants()
      loading.value = false
    })

    return { trek, participants, loading, error, form, submittingTrek, updateTrek, updateParticipantStatus, formatDate }
  }
}
</script>

<style scoped>
select option {
  background: var(--bg-color);
  color: var(--text-primary);
}
</style>
