<template>
  <div>
    <div class="page-header">
      <h1>Manage Staff</h1>
      <div class="actions" style="display: flex; gap: 1rem;">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search staff..." 
          class="premium-input"
          style="width: 250px;"
        >
        <button class="btn-premium btn-primary" @click="showAddModal = true">
          ➕ Add Staff
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
            <td>#{{ s.id }}</td>
            <td><strong>{{ s.name }}</strong></td>
            <td>{{ s.user?.username }}</td>
            <td>{{ s.contact_details }}</td>
            <td>
              <span class="badge" :class="s.status === 'Active' ? 'badge-success' : 'badge-danger'">
                {{ s.status }}
              </span>
            </td>
            <td>
              <button 
                @click="toggleStatus(s)"
                class="btn-premium"
                :class="s.status === 'Active' ? 'btn-danger' : 'btn-success'"
                style="padding: 0.4rem 0.8rem; font-size: 0.8rem;"
              >
                {{ s.status === 'Active' ? 'Deactivate' : 'Activate' }}
              </button>
            </td>
          </tr>
          <tr v-if="filteredStaff.length === 0">
            <td colspan="6" style="text-align: center; padding: 2rem;">No staff found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add Staff Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal-content glass-panel" style="padding: 2rem;">
        <h2>Add New Staff</h2>
        <form @submit.prevent="addStaff">
          <div class="form-group">
            <label>Name</label>
            <input type="text" v-model="newStaff.name" class="premium-input" required>
          </div>
          <div class="form-group">
            <label>Username</label>
            <input type="text" v-model="newStaff.username" class="premium-input" required>
          </div>
          <div class="form-group">
            <label>Email (Optional)</label>
            <input type="email" v-model="newStaff.email" class="premium-input">
          </div>
          <div class="form-group">
            <label>Password</label>
            <input type="password" v-model="newStaff.password" class="premium-input" required>
          </div>
          <div class="form-group">
            <label>Contact Details</label>
            <input type="text" v-model="newStaff.contact_details" class="premium-input">
          </div>
          
          <div style="display: flex; gap: 1rem; margin-top: 2rem; justify-content: flex-end;">
            <button type="button" class="btn-premium" @click="showAddModal = false" style="background: rgba(255,255,255,0.1); color: white;">Cancel</button>
            <button type="submit" class="btn-premium btn-primary" :disabled="submitting">
              {{ submitting ? 'Adding...' : 'Add Staff' }}
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'AdminStaff',
  setup() {
    const staff = ref([])
    const loading = ref(true)
    const error = ref('')
    const searchQuery = ref('')
    
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
      if(!confirm(`Are you sure you want to ${s.status === 'Active' ? 'deactivate' : 'activate'} this staff member?`)) return;
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch(`http://localhost:5000/api/admin/staff/${s.id}/status`, {
          method: 'PUT',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (!response.ok) throw new Error('Failed to update status')
        const updatedStaff = await response.json()
        const index = staff.value.findIndex(st => st.id === updatedStaff.id)
        if(index !== -1) staff.value[index] = updatedStaff
      } catch (err) {
        alert(err.message)
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
      } catch (err) {
        alert(err.message)
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
