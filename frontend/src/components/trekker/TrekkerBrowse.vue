<template>
  <div>
    <div class="page-header">
      <h1>Browse Treks</h1>
      <p style="color: var(--text-secondary); margin-top: 0.5rem;">Find and book your next adventure.</p>
    </div>

    <!-- Filters -->
    <div class="glass-panel" style="padding: 1.5rem; margin-bottom: 2rem; display: flex; gap: 1rem; flex-wrap: wrap;">
      <div style="flex: 1; min-width: 200px;">
        <input type="text" v-model="filters.search" placeholder="Search by name or location..." class="premium-input">
      </div>
      <div style="width: 150px;">
        <select v-model="filters.difficulty" class="premium-input">
          <option value="">Any Difficulty</option>
          <option value="Easy">Easy</option>
          <option value="Moderate">Moderate</option>
          <option value="Hard">Hard</option>
        </select>
      </div>
      <div style="width: 180px;">
        <select v-model="filters.duration" class="premium-input">
          <option value="">Any Duration</option>
          <option value="short">1 - 3 Days</option>
          <option value="medium">4 - 7 Days</option>
          <option value="long">8+ Days</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading treks...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else class="treks-grid">
      <div v-for="t in filteredTreks" :key="t.id" class="trek-card glass-panel">
        <div class="card-header">
          <img :src="getRandomTrekImage(t.id)" alt="Trek Image" style="width:80px;height:60px;object-fit:cover;border-radius:4px;margin-right:0.5rem;" />
          <h3>{{ t.name }}</h3>
          <span class="badge" 
            :class="{
              'badge-success': t.difficulty === 'Easy',
              'badge-warning': t.difficulty === 'Moderate',
              'badge-danger': t.difficulty === 'Hard'
            }"
          >
            {{ t.difficulty }}
          </span>
        </div>
        
        <div class="card-body">
          <p class="detail"><i class="icon">📍</i> {{ t.location }}</p>
          <p class="detail"><i class="icon">⏱️</i> {{ t.duration }} Days</p>
          <p class="detail"><i class="icon">📅</i> {{ t.start_date }}</p>
          <p class="detail"><i class="icon">🎟️</i> {{ t.available_slots }} Slots Available</p>
          <p class="detail"><i class="icon">💲</i> {{ t.price }} USD</p>
        </div>
        
        <div class="card-footer">
          <button @click="bookTrek(t)" class="btn-premium btn-primary" style="width: 100%;" :disabled="bookingInProgress === t.id">
            {{ bookingInProgress === t.id ? 'Booking...' : 'Book Now' }}
          </button>
        </div>
      </div>
      
      <div v-if="filteredTreks.length === 0" style="grid-column: 1 / -1; text-align: center; padding: 3rem;" class="glass-panel">
        <h3>No treks found.</h3>
        <p style="color: var(--text-secondary);">Try adjusting your search filters.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { getRandomTrekImage } from '../../composables/useRandomImage.js'
import { useConfirm } from '../../composables/useConfirm.js'
import { useToast } from '../../composables/useToast.js'

export default {
  name: 'TrekkerBrowse',
  setup() {
    const treks = ref([])
    const loading = ref(true)
    const error = ref('')
    const bookingInProgress = ref(null)
    const { showConfirm } = useConfirm()
    const { success, error: toastError } = useToast()

    const filters = ref({
      search: '',
      difficulty: '',
      duration: ''
    })

    const fetchTreks = async () => {
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch('/api/trekker/treks/open', {
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

    const filteredTreks = computed(() => {
      return treks.value.filter(t => {
        // Search filter
        const q = filters.value.search.toLowerCase()
        if (q && !t.name.toLowerCase().includes(q) && !t.location.toLowerCase().includes(q)) return false
        
        // Difficulty filter
        if (filters.value.difficulty && t.difficulty !== filters.value.difficulty) return false
        
        // Duration filter
        if (filters.value.duration === 'short' && t.duration > 3) return false
        if (filters.value.duration === 'medium' && (t.duration < 4 || t.duration > 7)) return false
        if (filters.value.duration === 'long' && t.duration < 8) return false
        
        return true
      })
    })

    const bookTrek = async (trek) => {
      const confirmed = await showConfirm({
        title: 'Confirm Booking',
        message: `Are you sure you want to book "${trek.name}"?`,
        confirmLabel: 'Book Now',
        confirmClass: 'btn-primary'
      })
      if (!confirmed) return
      
      bookingInProgress.value = trek.id
      try {
        const token = localStorage.getItem('tma_token')
        const response = await fetch('/api/trekker/bookings', {
          method: 'POST',
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ trek_id: trek.id })
        })
        
        const data = await response.json()
        if (!response.ok) throw new Error(data.msg || 'Failed to book trek')
        
        success(`"${trek.name}" booked successfully! Check your bookings tab.`)
        // Update local available slots
        trek.available_slots -= 1
      } catch (err) {
        toastError(err.message)
      } finally {
        bookingInProgress.value = null
      }
    }

    onMounted(fetchTreks)

    return { treks, loading, error, filters, filteredTreks, bookTrek, bookingInProgress, getRandomTrekImage }
  }
}
</script>

<style scoped>
select option {
  background: var(--bg-color);
  color: var(--text-primary);
}

.treks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.trek-card {
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.trek-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
}

.card-header {
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.card-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #fff;
}

.card-body {
  padding: 1.5rem;
  flex: 1;
}

.detail {
  margin: 0 0 0.75rem 0;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  font-size: 0.95rem;
}
.detail .icon {
  margin-right: 0.5rem;
  font-style: normal;
}

.card-footer {
  padding: 1.5rem;
  padding-top: 0;
}
</style>
