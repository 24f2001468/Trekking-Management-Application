<template>
  <div>
    <div class="page-header">
      <h1>Manage Users</h1>
      <div class="actions">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search by name or email..." 
          class="premium-input search-input"
        >
      </div>
    </div>

    <div v-if="loading" class="loading">Loading users...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else class="premium-table-wrapper">
      <table class="premium-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Email</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id">
            <td>#{{ user.id }}</td>
            <td><strong>{{ user.username }}</strong></td>
            <td>{{ user.email }}</td>
            <td>
              <span class="badge" :class="user.active ? 'badge-success' : 'badge-danger'">
                {{ user.active ? 'Active' : 'Blacklisted' }}
              </span>
            </td>
            <td>
              <button 
                @click="toggleStatus(user)"
                class="btn-premium"
                :class="user.active ? 'btn-danger' : 'btn-success'"
                style="padding: 0.5rem 1rem; font-size: 0.85rem;"
              >
                {{ user.active ? 'Deactivate' : 'Activate' }}
              </button>
            </td>
          </tr>
          <tr v-if="filteredUsers.length === 0">
            <td colspan="5" style="text-align: center; padding: 2rem;">No users found.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'AdminUsers',
  setup() {
    const users = ref([])
    const loading = ref(true)
    const error = ref('')
    const searchQuery = ref('')

    const fetchUsers = async () => {
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch('http://localhost:5000/api/admin/users', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (!response.ok) throw new Error('Failed to load users')
        users.value = await response.json()
      } catch (err) {
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    const toggleStatus = async (user) => {
      if(!confirm(`Are you sure you want to ${user.active ? 'deactivate' : 'activate'} this user?`)) return;
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch(`http://localhost:5000/api/admin/users/${user.id}/status`, {
          method: 'PUT',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (!response.ok) throw new Error('Failed to update status')
        const updatedUser = await response.json()
        const index = users.value.findIndex(u => u.id === updatedUser.id)
        if(index !== -1) users.value[index] = updatedUser
      } catch (err) {
        alert(err.message)
      }
    }

    const filteredUsers = computed(() => {
      const q = searchQuery.value.toLowerCase()
      if (!q) return users.value
      return users.value.filter(u => 
        u.username.toLowerCase().includes(q) || 
        u.email.toLowerCase().includes(q) ||
        u.id.toString().includes(q)
      )
    })

    onMounted(fetchUsers)

    return { users, loading, error, searchQuery, filteredUsers, toggleStatus }
  }
}
</script>

<style scoped>
.search-input {
  width: 300px;
}
</style>
