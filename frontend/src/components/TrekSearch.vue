<template>
  <div>
    <div class="page-header">
      <h1>Trek Search</h1>
      <p style="color: var(--text-secondary); margin-top: 0.5rem;">Advanced search and filter across all treks.</p>
    </div>

    <!-- Search / Filter Panel -->
    <div class="glass-panel search-panel">
      <div class="search-row">
        <div style="flex: 2; min-width: 200px;">
          <input
            type="text"
            v-model="filters.q"
            placeholder="Search by name or location..."
            class="premium-input"
            @keyup.enter="doSearch"
          >
        </div>
        <div style="flex: 1; min-width: 140px;">
          <select v-model="filters.status" class="premium-input">
            <option value="">Any Status</option>
            <option value="Pending">Pending</option>
            <option value="Approved">Approved</option>
            <option value="Open">Open</option>
            <option value="Closed">Closed</option>
            <option value="Completed">Completed</option>
          </select>
        </div>
        <div style="flex: 1; min-width: 140px;">
          <select v-model="filters.difficulty" class="premium-input">
            <option value="">Any Difficulty</option>
            <option value="Easy">Easy</option>
            <option value="Moderate">Moderate</option>
            <option value="Hard">Hard</option>
          </select>
        </div>
        <div style="flex: 1; min-width: 140px;">
          <input type="date" v-model="filters.from_date" class="premium-input" :title="'From date'">
        </div>
        <div style="flex: 1; min-width: 140px;">
          <input type="date" v-model="filters.to_date" class="premium-input" :title="'To date'">
        </div>
        <button @click="doSearch" class="btn-premium btn-primary" :disabled="loading">
          🔍 Search
        </button>
        <button @click="resetFilters" class="btn-premium" style="background: rgba(255,255,255,0.08); color: var(--text-secondary);">
          Reset
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">Searching treks...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else>
      <p v-if="searched" style="color: var(--text-secondary); margin-bottom: 1rem; font-size: 0.9rem;">
        {{ results.length }} result{{ results.length !== 1 ? 's' : '' }} found
      </p>
      
      <div class="premium-table-wrapper" v-if="results.length > 0">
        <table class="premium-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Location</th>
              <th>Difficulty</th>
              <th>Dates</th>
              <th>Status</th>
              <th>Slots</th>
              <th>Participants</th>
              <th>Staff</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in results" :key="t.id">
              <td data-label="ID">#{{ t.id }}</td>
              <td data-label="Name"><strong>{{ t.name }}</strong></td>
              <td data-label="Location">{{ t.location }}</td>
              <td data-label="Difficulty">
                <span class="badge"
                  :class="{
                    'badge-success': t.difficulty === 'Easy',
                    'badge-warning': t.difficulty === 'Moderate',
                    'badge-danger': t.difficulty === 'Hard'
                  }">
                  {{ t.difficulty }}
                </span>
              </td>
              <td data-label="Dates" style="font-size: 0.85rem;">{{ t.start_date }}<br>→ {{ t.end_date }}</td>
              <td data-label="Status">
                <span class="badge"
                  :class="{
                    'badge-success': t.status === 'Open',
                    'badge-warning': t.status === 'Pending' || t.status === 'Approved',
                    'badge-danger': t.status === 'Closed',
                    'badge-primary': t.status === 'Completed'
                  }">
                  {{ t.status }}
                </span>
              </td>
              <td data-label="Slots">{{ t.available_slots }}</td>
              <td data-label="Participants">{{ t.participants_count }}</td>
              <td data-label="Staff">{{ t.staff?.name || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else-if="searched" class="glass-panel" style="padding: 3rem; text-align: center;">
        <h3>No treks found</h3>
        <p style="color: var(--text-secondary);">Try adjusting your search filters.</p>
      </div>

      <div v-else class="glass-panel" style="padding: 3rem; text-align: center;">
        <h3>Search for Treks</h3>
        <p style="color: var(--text-secondary);">Use the filters above to find specific treks.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useToast } from '../composables/useToast.js'

export default {
  name: 'TrekSearch',
  setup() {
    const results = ref([])
    const loading = ref(false)
    const error = ref('')
    const searched = ref(false)
    const { error: toastError } = useToast()

    const filters = ref({
      q: '',
      status: '',
      difficulty: '',
      from_date: '',
      to_date: ''
    })

    const doSearch = async () => {
      loading.value = true
      error.value = ''
      try {
        const token = localStorage.getItem('tma_token')
        const params = new URLSearchParams()
        if (filters.value.q) params.set('q', filters.value.q)
        if (filters.value.status) params.set('status', filters.value.status)
        if (filters.value.difficulty) params.set('difficulty', filters.value.difficulty)
        if (filters.value.from_date) params.set('from_date', filters.value.from_date)
        if (filters.value.to_date) params.set('to_date', filters.value.to_date)

        const res = await fetch(`http://localhost:5000/api/treks/search?${params.toString()}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (!res.ok) throw new Error('Search failed')
        results.value = await res.json()
        searched.value = true
      } catch (err) {
        toastError(err.message)
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    const resetFilters = () => {
      filters.value = { q: '', status: '', difficulty: '', from_date: '', to_date: '' }
      results.value = []
      searched.value = false
      error.value = ''
    }

    return { filters, results, loading, error, searched, doSearch, resetFilters }
  }
}
</script>

<style scoped>
.search-panel {
  padding: 1.5rem;
  margin-bottom: 2rem;
}
.search-row {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  align-items: flex-end;
}
</style>
