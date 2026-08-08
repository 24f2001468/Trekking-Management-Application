<template>
  <div>
    <div class="page-header">
      <h1>Manage Treks</h1>
      <button class="btn-premium btn-primary" @click="openCreateModal">
        <i class="bi bi-plus-lg"></i> New Trek
      </button>
    </div>

    <div v-if="loading" class="loading">Loading treks…</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else class="premium-table-wrapper">
      <table class="premium-table">
        <thead>
          <tr>
            <th>Image</th>
            <th>ID</th>
            <th>Name</th>
            <th>Location</th>
            <th>Difficulty</th>
            <th>Dates</th>
            <th>Status</th>
            <th>Staff</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in treks" :key="t.id">
            <td data-label="Image"><img :src="getRandomTrekImage(t.id)" alt="Trek Image" style="width:60px;height:40px;object-fit:cover;border-radius:4px;"/></td>
            <td data-label="ID">#{{ t.id }}</td>
            <td data-label="Name"><strong>{{ t.name }}</strong></td>
            <td data-label="Location">{{ t.location }}</td>
            <td data-label="Difficulty">
              <span class="badge" :class="{'badge-success':t.difficulty==='Easy','badge-warning':t.difficulty==='Moderate','badge-danger':t.difficulty==='Hard'}">{{ t.difficulty }}</span>
            </td>
            <td data-label="Dates" class="date-cell">{{ t.start_date }}<br><span class="muted">→ {{ t.end_date }}</span></td>
            <td data-label="Status"><span class="badge badge-primary">{{ t.status }}</span></td>
            <td data-label="Staff">
              <span v-if="t.staff">{{ t.staff.name }}</span>
              <button v-else class="btn-premium btn-ghost btn-sm" @click="openAssignModal(t)">Assign</button>
            </td>
            <td data-label="Actions">
              <div class="action-row">
                <button class="btn-premium btn-ghost btn-sm" @click="openEditModal(t)" title="Edit"><i class="bi bi-pencil-fill"></i></button>
                <button class="btn-premium btn-danger btn-sm" @click="deleteTrek(t.id)" title="Delete"><i class="bi bi-trash3-fill"></i></button>
              </div>
            </td>
          </tr>
          <tr v-if="treks.length === 0">
            <td colspan="8" class="empty-cell">No treks found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Trek Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-content glass-panel modal-pad">
        <div class="modal-header-row">
          <h2>{{ editingTrek ? 'Edit Trek' : 'New Trek' }}</h2>
          <button class="btn-premium btn-ghost btn-sm" @click="showModal=false"><i class="bi bi-x-lg"></i></button>
        </div>
        <form @submit.prevent="saveTrek">
          <div class="form-group">
            <label>Name</label>
            <input type="text" v-model="form.name" class="premium-input" required placeholder="Trek name">
          </div>
          <div class="form-group">
            <label>Location</label>
            <input type="text" v-model="form.location" class="premium-input" required placeholder="Location">
          </div>
          <div class="form-row-2">
            <div class="form-group">
              <label>Difficulty</label>
              <select v-model="form.difficulty" class="premium-input" required>
                <option value="Easy">Easy</option>
                <option value="Moderate">Moderate</option>
                <option value="Hard">Hard</option>
              </select>
            </div>
            <div class="form-group">
              <label>Duration (days)</label>
              <input type="number" v-model="form.duration" class="premium-input" required min="1">
            </div>
          </div>
          <div class="form-row-2">
            <div class="form-group">
              <label>Start Date</label>
              <input type="date" v-model="form.start_date" class="premium-input" required>
            </div>
            <div class="form-group">
              <label>End Date</label>
              <input type="date" v-model="form.end_date" class="premium-input" required>
            </div>
          </div>
          <div class="form-row-2">
            <div class="form-group">
              <label>Slots</label>
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
          <div class="modal-footer-row">
            <button type="button" class="btn-premium btn-ghost" @click="showModal=false">Cancel</button>
            <button type="submit" class="btn-premium btn-primary" :disabled="submitting">
              {{ submitting ? 'Saving…' : 'Save Trek' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Assign Staff Modal -->
    <div v-if="showAssignModal" class="modal-overlay" @click.self="showAssignModal = false">
      <div class="modal-content glass-panel modal-pad">
        <div class="modal-header-row">
          <h2>Assign Staff</h2>
          <button class="btn-premium btn-ghost btn-sm" @click="showAssignModal=false"><i class="bi bi-x-lg"></i></button>
        </div>
        <p class="muted" style="margin:0 0 1.25rem;">Trek: <strong>{{ selectedTrek?.name }}</strong></p>
        <div class="form-group">
          <label>Staff Member</label>
          <select v-model="selectedStaffId" class="premium-input">
            <option value="">— Unassigned —</option>
            <option v-for="s in staffList" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
        </div>
        <div class="modal-footer-row">
          <button type="button" class="btn-premium btn-ghost" @click="showAssignModal=false">Cancel</button>
          <button type="button" class="btn-premium btn-primary" @click="assignStaff" :disabled="submitting">
            {{ submitting ? 'Assigning…' : 'Assign' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { getRandomTrekImage } from '../../composables/useRandomImage.js'
import { useToast } from '../../composables/useToast.js'
const API = 'http://localhost:5000'
const tok = () => localStorage.getItem('tma_token')
export default {
  name: 'AdminTreks',
  setup() {
    const treks=ref([]), loading=ref(true), error=ref('')
    const { showConfirm } = useConfirm()
    const { success, error:toastError } = useToast()
    const showModal=ref(false), editingTrek=ref(null), submitting=ref(false)
    const form=ref({ name:'',location:'',difficulty:'Easy',duration:1,available_slots:10,start_date:'',end_date:'',status:'Open' })
    const showAssignModal=ref(false), selectedTrek=ref(null), selectedStaffId=ref(''), staffList=ref([])

    const fetchTreks = async () => {
      try {
        const r = await fetch(`${API}/api/admin/treks`,{headers:{Authorization:`Bearer ${tok()}`}})
        if(!r.ok) throw new Error('Failed to load treks')
        treks.value = await r.json()
      } catch(e){error.value=e.message} finally{loading.value=false}
    }
    const fetchStaff = async () => {
      try {
        const r = await fetch(`${API}/api/admin/staff`,{headers:{Authorization:`Bearer ${tok()}`}})
        if(r.ok){ const d=await r.json(); staffList.value=d.filter(s=>s.status==='Active') }
      } catch(e){ console.error(e) }
    }
    const openCreateModal=()=>{ editingTrek.value=null; form.value={name:'',location:'',difficulty:'Easy',duration:1,available_slots:10,start_date:'',end_date:'',status:'Open'}; showModal.value=true }
    const openEditModal=(t)=>{ editingTrek.value=t; form.value={...t}; showModal.value=true }
    const saveTrek=async()=>{
      submitting.value=true
      try {
        const isEdit=!!editingTrek.value
        const url=isEdit?`${API}/api/admin/treks/${editingTrek.value.id}`:`${API}/api/admin/treks`
        const r=await fetch(url,{method:isEdit?'PUT':'POST',headers:{Authorization:`Bearer ${tok()}`,'Content-Type':'application/json'},body:JSON.stringify(form.value)})
        const d=await r.json(); if(!r.ok) throw new Error(d.msg||'Failed')
        if(isEdit){const i=treks.value.findIndex(t=>t.id===d.id);if(i!==-1)treks.value[i]=d;success('Trek updated.')}
        else{treks.value.push(d);success('Trek created.')}
        showModal.value=false
      } catch(e){toastError(e.message)} finally{submitting.value=false}
    }
    const deleteTrek=async(id)=>{
      if(!await showConfirm({title:'Delete Trek',message:'Delete this trek and all its bookings?',confirmLabel:'Delete',confirmClass:'btn-danger'})) return
      try {
        const r=await fetch(`${API}/api/admin/treks/${id}`,{method:'DELETE',headers:{Authorization:`Bearer ${tok()}`}})
        if(!r.ok) throw new Error('Failed'); treks.value=treks.value.filter(t=>t.id!==id); success('Trek deleted.')
      } catch(e){toastError(e.message)}
    }
    const openAssignModal=(t)=>{ selectedTrek.value=t; selectedStaffId.value=t.assigned_staff_id||''; showAssignModal.value=true }
    const assignStaff=async()=>{
      submitting.value=true
      try {
        const r=await fetch(`${API}/api/admin/treks/${selectedTrek.value.id}/assign`,{method:'PUT',headers:{Authorization:`Bearer ${tok()}`,'Content-Type':'application/json'},body:JSON.stringify({staff_id:selectedStaffId.value||null})})
        const d=await r.json(); if(!r.ok) throw new Error(d.msg||'Failed')
        const i=treks.value.findIndex(t=>t.id===d.id); if(i!==-1)treks.value[i]=d
        showAssignModal.value=false; success('Staff assigned.')
      } catch(e){toastError(e.message)} finally{submitting.value=false}
    }
    onMounted(()=>{ fetchTreks(); fetchStaff() })
    return { treks, loading, error, showModal, editingTrek, form, submitting, openCreateModal, openEditModal, saveTrek, deleteTrek, showAssignModal, selectedTrek, selectedStaffId, staffList, openAssignModal, assignStaff, getRandomTrekImage }
  }
}
</script>

<style scoped>
.date-cell { font-size:.82rem; line-height:1.5; }
.muted { color:var(--text-3); font-size:.82rem; }
.action-row { display:flex; gap:.4rem; }
.empty-cell { text-align:center; padding:2.5rem; color:var(--text-2); }
.modal-pad { padding:1.75rem; }
.modal-header-row { display:flex; justify-content:space-between; align-items:center; margin-bottom:1.25rem; }
.modal-header-row h2 { margin:0; font-size:1.2rem; }
.modal-footer-row { display:flex; justify-content:flex-end; gap:.75rem; margin-top:1.5rem; }
.form-row-2 { display:grid; grid-template-columns:1fr 1fr; gap:.9rem; }
@media(max-width:480px) { .form-row-2 { grid-template-columns:1fr; } }
</style>
