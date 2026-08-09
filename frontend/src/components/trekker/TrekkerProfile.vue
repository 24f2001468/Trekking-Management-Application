<template>
  <div>
    <div class="page-header">
      <h1>My Profile</h1>
      <p>Update your account details and password.</p>
    </div>

    <div class="profile-grid">

      <!-- ── Account Info ── -->
      <div class="glass-panel section-card">
        <h3 class="section-title">?? Account Details</h3>

        <div v-if="infoSuccess" class="alert-ok">{{ infoSuccess }}</div>
        <div v-if="infoError"   class="alert-err">{{ infoError }}</div>

        <form @submit.prevent="updateInfo">
          <div class="form-group">
            <label>Username</label>
            <input type="text" v-model="form.username" class="premium-input"
              required minlength="3" placeholder="Your username">
          </div>
          <div class="form-group">
            <label>Email Address</label>
            <input type="email" v-model="form.email" class="premium-input"
              required placeholder="your@email.com">
          </div>
          <button type="submit" class="btn-premium btn-primary" :disabled="savingInfo">
            {{ savingInfo ? 'Saving…' : 'Save Changes' }}
          </button>
        </form>
      </div>

      <!-- ── Change Password ── -->
      <div class="glass-panel section-card">
        <h3 class="section-title">?? Change Password</h3>

        <div v-if="pwSuccess" class="alert-ok">{{ pwSuccess }}</div>
        <div v-if="pwError"   class="alert-err">{{ pwError }}</div>

        <form @submit.prevent="updatePassword">
          <div class="form-group">
            <label>Current Password</label>
            <input type="password" v-model="pwForm.current_password" class="premium-input"
              required placeholder="Enter current password">
          </div>
          <div class="form-group">
            <label>New Password</label>
            <input type="password" v-model="pwForm.new_password" class="premium-input"
              required minlength="6" placeholder="Min. 6 characters">
          </div>
          <div class="form-group">
            <label>Confirm New Password</label>
            <input type="password" v-model="pwForm.confirm_password" class="premium-input"
              required placeholder="Repeat new password">
          </div>
          <button type="submit" class="btn-premium btn-success" :disabled="savingPw">
            {{ savingPw ? 'Updating…' : 'Update Password' }}
          </button>
        </form>
      </div>

      <!-- ── Account Stats ── -->
      <div class="glass-panel section-card stats-card" v-if="profile">
        <h3 class="section-title">? Account Info</h3>
        <div class="info-row"><span>User ID</span><strong>#{{ profile.id }}</strong></div>
        <div class="info-row"><span>Role</span><strong>{{ profile.role }}</strong></div>
        <div class="info-row">
          <span>Status</span>
          <span class="badge" :class="profile.active ? 'badge-success' : 'badge-danger'">
            {{ profile.active ? 'Active' : 'Inactive' }}
          </span>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useToast } from '../../composables/useToast.js'

const API = 'http://localhost:5000'
const tok = () => localStorage.getItem('tma_token')

export default {
  name: 'TrekkerProfile',
  setup() {
    const profile = ref(null)
    const { success } = useToast()

    const form = ref({ username: '', email: '' })
    const infoSuccess = ref(''), infoError = ref(''), savingInfo = ref(false)

    const pwForm = ref({ current_password: '', new_password: '', confirm_password: '' })
    const pwSuccess = ref(''), pwError = ref(''), savingPw = ref(false)

    const fetchProfile = async () => {
      try {
        const r = await fetch(`${API}/api/auth/profile`, {
          headers: { Authorization: `Bearer ${tok()}` }
        })
        if (!r.ok) throw new Error('Failed to load profile')
        profile.value = await r.json()
        form.value.username = profile.value.username
        form.value.email    = profile.value.email
      } catch (e) { infoError.value = e.message }
    }

    const updateInfo = async () => {
      infoSuccess.value = ''; infoError.value = ''; savingInfo.value = true
      try {
        const r = await fetch(`${API}/api/auth/profile`, {
          method: 'PUT',
          headers: { Authorization: `Bearer ${tok()}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: form.value.username, email: form.value.email })
        })
        const d = await r.json()
        if (!r.ok) throw new Error(d.msg || 'Update failed')
        profile.value = d.user
        // Update stored username in localStorage
        const stored = JSON.parse(localStorage.getItem('tma_user') || '{}')
        stored.username = d.user.username
        localStorage.setItem('tma_user', JSON.stringify(stored))
        infoSuccess.value = 'Profile updated successfully.'
        success('Profile updated.')
      } catch (e) { infoError.value = e.message }
      finally { savingInfo.value = false }
    }

    const updatePassword = async () => {
      pwSuccess.value = ''; pwError.value = ''; 
      if (pwForm.value.new_password !== pwForm.value.confirm_password) {
        pwError.value = 'New passwords do not match.'; return
      }
      savingPw.value = true
      try {
        const r = await fetch(`${API}/api/auth/profile`, {
          method: 'PUT',
          headers: { Authorization: `Bearer ${tok()}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({
            current_password: pwForm.value.current_password,
            new_password:     pwForm.value.new_password
          })
        })
        const d = await r.json()
        if (!r.ok) throw new Error(d.msg || 'Password update failed')
        pwSuccess.value = 'Password changed successfully.'
        pwForm.value = { current_password: '', new_password: '', confirm_password: '' }
        success('Password updated.')
      } catch (e) { pwError.value = e.message }
      finally { savingPw.value = false }
    }

    onMounted(fetchProfile)
    return { profile, form, infoSuccess, infoError, savingInfo, updateInfo,
             pwForm, pwSuccess, pwError, savingPw, updatePassword }
  }
}
</script>

<style scoped>
.profile-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}
.stats-card { grid-column: 1 / -1; }
.section-card { padding: 1.75rem; }
.section-title {
  margin: 0 0 1.5rem;
  font-size: 1rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: .55rem;
  color: var(--text-1);
  border-bottom: 1px solid var(--border);
  padding-bottom: .75rem;
}
.alert-ok {
  background: var(--ok-bg);
  border: 1px solid rgba(79,168,124,.3);
  color: #6dbf95;
  padding: .7rem 1rem;
  border-radius: var(--r-s);
  font-size: .875rem;
  margin-bottom: 1.1rem;
}
.alert-err {
  background: var(--err-bg);
  border: 1px solid rgba(217,107,85,.3);
  color: #f0a090;
  padding: .7rem 1rem;
  border-radius: var(--r-s);
  font-size: .875rem;
  margin-bottom: 1.1rem;
}
.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: .65rem 0;
  border-bottom: 1px solid var(--border);
  font-size: .9rem;
}
.info-row:last-child { border-bottom: none; }
.info-row span:first-child { color: var(--text-2); }
@media (max-width: 640px) {
  .profile-grid { grid-template-columns: 1fr; }
  .stats-card { grid-column: 1; }
}
</style>
