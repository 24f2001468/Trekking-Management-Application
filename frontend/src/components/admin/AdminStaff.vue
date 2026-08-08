<template>
  <div>
    <div class="page-header">
      <h1>Manage Staff</h1>
      <div style="display:flex;gap:.75rem;flex-wrap:wrap;align-items:center;">
        <input type="text" v-model="searchQuery" placeholder="Search staff…" class="premium-input" style="width:220px;">
        <button class="btn-premium btn-primary" @click="showAddModal = true">
          <i class="bi bi-person-plus-fill"></i> Add Staff
        </button>
      </div>
    </div>

    <!-- Staff Table -->
    <div v-if="loading" class="loading">Loading staff...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="premium-table-wrapper">
      <table class="premium-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Username</th>
            <th>Contact</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in filteredStaff" :key="s.id">
            <td data-label="ID">#{{ s.id }}</td>
            <td data-label="Name"><strong>{{ s.name }}</strong></td>
            <td data-label="Username">{{ s.user?.username }}</td>
            <td data-label="Contact">{{ s.contact_details }}</td>
            <td data-label="Status">
              <span class="badge" :class="s.status === 'Active' ? 'badge-success' : 'badge-danger'">{{ s.status }}</span>
            </td>
            <td data-label="Actions">
              <button @click="toggleStatus(s)" class="btn-premium btn-sm" :class="s.status==='Active'?'btn-danger':'btn-success'">
                {{ s.status === 'Active' ? 'Deactivate' : 'Activate' }}
              </button>
            </td>
          </tr>
          <tr v-if="filteredStaff.length === 0">
            <td colspan="6" style="text-align:center;padding:2rem;color:var(--text-2);">No staff found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add Staff Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal-content glass-panel modal-pad">
        <div class="modal-hdr">
          <h2>Add New Staff</h2>
          <button class="btn-premium btn-ghost btn-sm" @click="showAddModal=false"><i class="bi bi-x-lg"></i></button>
        </div>
        <form @submit.prevent="addStaff">
          <div class="form-group">
            <label>Full Name</label>
            <input type="text" v-model="newStaff.name" class="premium-input" required placeholder="Staff full name">
          </div>
          <div class="form-row-2">
            <div class="form-group">
              <label>Username</label>
              <input type="text" v-model="newStaff.username" class="premium-input" required placeholder="Login username">
            </div>
            <div class="form-group">
              <label>Password</label>
              <input type="password" v-model="newStaff.password" class="premium-input" required placeholder="Initial password">
            </div>
          </div>
          <div class="form-group">
            <label>Email (optional)</label>
            <input type="email" v-model="newStaff.email" class="premium-input" placeholder="staff@example.com">
          </div>
          <div class="form-group">
            <label>Contact Details</label>
            <input type="text" v-model="newStaff.contact_details" class="premium-input" placeholder="Phone / other">
          </div>
          <div class="modal-ftr">
            <button type="button" class="btn-premium btn-ghost" @click="showAddModal=false">Cancel</button>
            <button type="submit" class="btn-premium btn-primary" :disabled="submitting">
              {{ submitting ? 'Adding…' : 'Add Staff' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useConfirm } from '../../composables/useConfirm.js'
import { useToast } from '../../composables/useToast.js'

export default {
  name: 'AdminStaff',
  setup() {
    const staff = ref([])
    const loading = ref(true)
    const error = ref('')
    const searchQuery = ref('')
    const { showConfirm } = useConfirm()
    const { success, error: toastError } = useToast()
    
    const showAddModal = ref(false)
    const submitting = ref(false)
    const newStaff = ref({ name: '', username: '', email: '', password: '', contact_details: '' })

    const fetchStaff = async () => {
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch('http://localhost:5000/api/admin/staff', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (!response.ok) throw new Error('Failed to load staff')
        staff.value = await response.json()
      } catch (err) {
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    const toggleStatus = async (s) => {
      const isActive = s.status === 'Active'
      const confirmed = await showConfirm({
        title: isActive ? 'Deactivate Staff' : 'Activate Staff',
        message: `Are you sure you want to ${isActive ? 'deactivate' : 'activate'} ${s.name}?`,
        confirmLabel: isActive ? 'Deactivate' : 'Activate',
        confirmClass: isActive ? 'btn-danger' : 'btn-success'
      })
      if (!confirmed) return
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch(`http://localhost:5000/api/admin/staff/${s.id}/status`, {
          method: 'PUT',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (!response.ok) throw new Error('Failed to update status')
        const updatedStaff = await response.json()
        const index = staff.value.findIndex(st => st.id === updatedStaff.id)
        if (index !== -1) staff.value[index] = updatedStaff
        success(`Staff member ${isActive ? 'deactivated' : 'activated'}.`)
      } catch (err) {
        toastError(err.message)
      }
    }

    const addStaff = async () => {
      submitting.value = true
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch('http://localhost:5000/api/admin/staff', {
          method: 'POST',
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(newStaff.value)
        })
        const data = await response.json()
        if (!response.ok) throw new Error(data.msg || 'Failed to add staff')
        
        staff.value.push(data)
        showAddModal.value = false
        newStaff.value = { name: '', username: '', email: '', password: '', contact_details: '' }
        success('Staff member added successfully.')
      } catch (err) {
        toastError(err.message)
      } finally {
        submitting.value = false
      }
    }

    const filteredStaff = computed(() => {
      const q = searchQuery.value.toLowerCase()
      if (!q) return staff.value
      return staff.value.filter(s => 
        s.name.toLowerCase().includes(q) || 
        (s.user && s.user.username.toLowerCase().includes(q))
      )
    })

    onMounted(fetchStaff)

    return { staff, loading, error, searchQuery, filteredStaff, toggleStatus, showAddModal, newStaff, addStaff, submitting }
  }
}
</script>
