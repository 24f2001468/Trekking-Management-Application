<template>
  <div>
    <div class="page-header">
      <h1>Manage Treks</h1>
      <button class="btn-premium btn-primary" @click="openCreateModal">
        ➕ Create New Trek
      </button>
    </div>

    <div v-if="loading" class="loading">Loading treks...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else class="premium-table-wrapper">
      <table class="premium-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Location</th>
            <th>Difficulty</th>
            <th>Dates</th>
            <th>Status</th>
            <th>Staff Assigned</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in treks" :key="t.id">
            <td>#{{ t.id }}</td>
            <td><strong>{{ t.name }}</strong></td>
            <td>{{ t.location }}</td>
            <td>
              <span class="badge" 
                :class="{
                  'badge-success': t.difficulty === 'Easy',
                  'badge-warning': t.difficulty === 'Moderate',
                  'badge-danger': t.difficulty === 'Hard'
                }">
                {{ t.difficulty }}
              </span>
            </td>
            <td style="font-size: 0.85rem;">{{ t.start_date }} <br>to<br> {{ t.end_date }}</td>
            <td>{{ t.status }}</td>
            <td>
              <div v-if="t.staff">{{ t.staff.name }}</div>
              <button v-else class="btn-premium" style="padding: 0.2rem 0.5rem; font-size: 0.7rem; background: rgba(59,130,246,0.2); color: #60a5fa;" @click="openAssignModal(t)">
                Assign Staff
              </button>
            </td>
            <td>
              <div style="display: flex; gap: 0.5rem;">
                <button class="btn-premium" style="padding: 0.4rem; background: rgba(255,255,255,0.1); color: white;" @click="openEditModal(t)" title="Edit">✏️</button>
                <button class="btn-premium" style="padding: 0.4rem; background: rgba(239,68,68,0.2); color: #f87171;" @click="deleteTrek(t.id)" title="Delete">🗑️</button>
              </div>
            </td>
          </tr>
          <tr v-if="treks.length === 0">
            <td colspan="8" style="text-align: center; padding: 2rem;">No treks found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create/Edit Trek Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-content glass-panel" style="padding: 2rem;">
        <h2>{{ editingTrek ? 'Edit Trek' : 'Create New Trek' }}</h2>
        <form @submit.prevent="saveTrek">
          <div class="form-group">
            <label>Name</label>
            <input type="text" v-model="form.name" class="premium-input" required>
          </div>
          <div class="form-group">
            <label>Location</label>
            <input type="text" v-model="form.location" class="premium-input" required>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label>Difficulty</label>
              <select v-model="form.difficulty" class="premium-input" required>
                <option value="Easy">Easy</option>
                <option value="Moderate">Moderate</option>
                <option value="Hard">Hard</option>
              </select>
            </div>
            <div class="form-group">
              <label>Duration (Days)</label>
              <input type="number" v-model="form.duration" class="premium-input" required min="1">
            </div>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label>Start Date</label>
              <input type="date" v-model="form.start_date" class="premium-input" required>
            </div>
            <div class="form-group">
              <label>End Date</label>
              <input type="date" v-model="form.end_date" class="premium-input" required>
            </div>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="form-group">
              <label>Available Slots</label>
              <input type="number" v-model="form.available_slots" class="premium-input" required min="1">
            </div>
            <div class="form-group">
              <label>Status</label>
              <select v-model="form.status" class="premium-input" required>
                <option value="Pending">Pending</option>
                <option value="Approved">Approved</option>
                <option value="Open">Open</option>
                <option value="Closed">Closed</option>
                <option value="Completed">Completed</option>
              </select>
            </div>
          </div>

          <div style="display: flex; gap: 1rem; margin-top: 1.5rem; justify-content: flex-end;">
            <button type="button" class="btn-premium" @click="showModal = false" style="background: rgba(255,255,255,0.1); color: white;">Cancel</button>
            <button type="submit" class="btn-premium btn-primary" :disabled="submitting">
              {{ submitting ? 'Saving...' : 'Save Trek' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Assign Staff Modal -->
    <div v-if="showAssignModal" class="modal-overlay" @click.self="showAssignModal = false">
      <div class="modal-content glass-panel" style="padding: 2rem;">
        <h2>Assign Staff to {{ selectedTrek?.name }}</h2>
        <div class="form-group">
          <label>Select Staff Member</label>
          <select v-model="selectedStaffId" class="premium-input">
            <option value="">-- No Staff --</option>
            <option v-for="s in staffList" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
        </div>
        <div style="display: flex; gap: 1rem; margin-top: 2rem; justify-content: flex-end;">
          <button type="button" class="btn-premium" @click="showAssignModal = false" style="background: rgba(255,255,255,0.1); color: white;">Cancel</button>
          <button type="button" class="btn-premium btn-primary" @click="assignStaff" :disabled="submitting">
            {{ submitting ? 'Assigning...' : 'Assign' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'AdminTreks',
  setup() {
    const treks = ref([])
    const loading = ref(true)
    const error = ref('')
    
    const showModal = ref(false)
    const editingTrek = ref(null)
    const form = ref({
      name: '', location: '', difficulty: 'Easy', duration: 1,
      available_slots: 10, start_date: '', end_date: '', status: 'Open'
    })
    const submitting = ref(false)

    const showAssignModal = ref(false)
    const selectedTrek = ref(null)
    const selectedStaffId = ref('')
    const staffList = ref([])

    const fetchTreks = async () => {
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch('http://localhost:5000/api/admin/treks', {
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

    const fetchStaff = async () => {
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch('http://localhost:5000/api/admin/staff', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (response.ok) {
          const allStaff = await response.json()
          staffList.value = allStaff.filter(s => s.status === 'Active')
        }
      } catch (err) {
        console.error("Failed to load staff", err)
      }
    }

    const openCreateModal = () => {
      editingTrek.value = null
      form.value = { name: '', location: '', difficulty: 'Easy', duration: 1, available_slots: 10, start_date: '', end_date: '', status: 'Open' }
      showModal.value = true
    }

    const openEditModal = (t) => {
      editingTrek.value = t
      form.value = { ...t }
      showModal.value = true
    }

    const saveTrek = async () => {
      submitting.value = true
      try {
        const token = localStorage.getItem('tma_token')
        const isEdit = !!editingTrek.value
        const url = isEdit ? `http://localhost:5000/api/admin/treks/${editingTrek.value.id}` : `http://localhost:5000/api/admin/treks`
        const method = isEdit ? 'PUT' : 'POST'
        
        const response = await fetch(url, {
          method,
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(form.value)
        })
        
        const data = await response.json()
        if (!response.ok) throw new Error(data.msg || 'Failed to save trek')
        
        if (isEdit) {
          const index = treks.value.findIndex(t => t.id === data.id)
          if(index !== -1) treks.value[index] = data
        } else {
          treks.value.push(data)
        }
        showModal.value = false
      } catch (err) {
        alert(err.message)
      } finally {
        submitting.value = false
      }
    }

    const deleteTrek = async (id) => {
      if(!confirm("Are you sure you want to delete this trek?")) return;
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch(`http://localhost:5000/api/admin/treks/${id}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (!response.ok) throw new Error('Failed to delete trek')
        treks.value = treks.value.filter(t => t.id !== id)
      } catch (err) {
        alert(err.message)
      }
    }

    const openAssignModal = (t) => {
      selectedTrek.value = t
      selectedStaffId.value = t.assigned_staff_id || ''
      showAssignModal.value = true
    }

    const assignStaff = async () => {
      submitting.value = true
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch(`http://localhost:5000/api/admin/treks/${selectedTrek.value.id}/assign`, {
          method: 'PUT',
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ staff_id: selectedStaffId.value || null })
        })
        
        const data = await response.json()
        if (!response.ok) throw new Error(data.msg || 'Failed to assign staff')
        
        const index = treks.value.findIndex(t => t.id === data.id)
        if(index !== -1) treks.value[index] = data
        showAssignModal.value = false
      } catch (err) {
        alert(err.message)
      } finally {
        submitting.value = false
      }
    }

    onMounted(() => {
      fetchTreks()
      fetchStaff()
    })

    return { 
      treks, loading, error, 
      showModal, editingTrek, form, submitting, openCreateModal, openEditModal, saveTrek, deleteTrek,
      showAssignModal, selectedTrek, selectedStaffId, staffList, openAssignModal, assignStaff
    }
  }
}
</script>

<style scoped>
select option {
  background: var(--bg-color);
  color: var(--text-primary);
}
</style>
