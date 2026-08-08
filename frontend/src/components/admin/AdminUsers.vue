<template>
  <div>
    <div class="page-header">
      <h1>Manage Users</h1>
      <input type="text" v-model="searchQuery" placeholder="Search by username or email…"
        class="premium-input" style="width:260px;">
    </div>

    <div v-if="loading" class="loading">Loading users…</div>
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
            <td data-label="ID">#{{ user.id }}</td>
            <td data-label="Username"><strong>{{ user.username }}</strong></td>
            <td data-label="Email">{{ user.email }}</td>
            <td data-label="Status">
              <span v-if="user.is_blacklisted" class="badge badge-danger">Blacklisted</span>
              <span v-else-if="!user.active" class="badge badge-warning">Inactive</span>
              <span v-else class="badge badge-success">Active</span>
            </td>
            <td data-label="Actions">
              <div style="display:flex;gap:.4rem;flex-wrap:wrap;">
                <!-- Deactivate / Activate -->
                <button
                  v-if="!user.is_blacklisted"
                  @click="toggleStatus(user)"
                  class="btn-premium btn-sm"
                  :class="user.active ? 'btn-warning' : 'btn-success'">
                  {{ user.active ? 'Deactivate' : 'Activate' }}
                </button>
                <!-- Blacklist / Unblacklist -->
                <button
                  @click="toggleBlacklist(user)"
                  class="btn-premium btn-sm"
                  :class="user.is_blacklisted ? 'btn-success' : 'btn-danger'">
                  {{ user.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="filteredUsers.length === 0">
            <td colspan="5" style="text-align:center;padding:2rem;color:var(--text-2);">No users found.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useConfirm } from '../../composables/useConfirm.js'
import { useToast } from '../../composables/useToast.js'

const API = 'http://localhost:5000'
const tok = () => localStorage.getItem('tma_token')

export default {
  name: 'AdminUsers',
  setup() {
    const users = ref([]), loading = ref(true), error = ref(''), searchQuery = ref('')
    const { showConfirm } = useConfirm()
    const { success, error: toastError } = useToast()

    const fetchUsers = async () => {
      try {
        const r = await fetch(`${API}/api/admin/users`, { headers: { Authorization: `Bearer ${tok()}` } })
        if (!r.ok) throw new Error('Failed to load users')
        users.value = await r.json()
      } catch (e) { error.value = e.message } finally { loading.value = false }
    }

    const toggleStatus = async (user) => {
      const isActive = user.active
      const ok = await showConfirm({
        title: isActive ? 'Deactivate User' : 'Activate User',
        message: `${isActive ? 'Deactivate' : 'Re-activate'} account for "${user.username}"? This is reversible.`,
        confirmLabel: isActive ? 'Deactivate' : 'Activate',
        confirmClass: isActive ? 'btn-warning' : 'btn-success'
      })
      if (!ok) return
      try {
        const r = await fetch(`${API}/api/admin/users/${user.id}/status`, {
          method: 'PUT', headers: { Authorization: `Bearer ${tok()}` }
        })
        if (!r.ok) throw new Error('Failed')
        const d = await r.json()
        const i = users.value.findIndex(u => u.id === d.id)
        if (i !== -1) users.value[i] = d
        success(`"${d.username}" ${d.active ? 'activated' : 'deactivated'}.`)
      } catch (e) { toastError(e.message) }
    }

    const toggleBlacklist = async (user) => {
      const isBL = user.is_blacklisted
      const ok = await showConfirm({
        title: isBL ? 'Remove Blacklist' : 'Blacklist User',
        message: isBL
          ? `Remove the permanent ban on "${user.username}"?`
          : `Permanently blacklist "${user.username}"? They will not be able to log in.`,
        confirmLabel: isBL ? 'Unblacklist' : 'Blacklist',
        confirmClass: isBL ? 'btn-success' : 'btn-danger'
      })
      if (!ok) return
      try {
        const r = await fetch(`${API}/api/admin/users/${user.id}/blacklist`, {
          method: 'PUT', headers: { Authorization: `Bearer ${tok()}` }
        })
        if (!r.ok) throw new Error('Failed')
        const d = await r.json()
        const i = users.value.findIndex(u => u.id === d.id)
        if (i !== -1) users.value[i] = d
        success(`"${d.username}" ${d.is_blacklisted ? 'blacklisted' : 'removed from blacklist'}.`)
      } catch (e) { toastError(e.message) }
    }

    const filteredUsers = computed(() => {
      const q = searchQuery.value.toLowerCase()
      if (!q) return users.value
      return users.value.filter(u =>
        u.username.toLowerCase().includes(q) ||
        u.email.toLowerCase().includes(q) ||
        String(u.id).includes(q)
      )
    })

    onMounted(fetchUsers)
    return { users, loading, error, searchQuery, filteredUsers, toggleStatus, toggleBlacklist }
  }
}
</script>
