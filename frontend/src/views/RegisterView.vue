<template>
  <div class="auth-page">
    <div class="auth-card glass-panel">
      <div class="auth-logo">
        <span class="icon-wrap">🏔️</span>
        <span class="logo-name">TMA</span>
      </div>
      <h2 class="auth-title">Create Account</h2>
      <p class="auth-subtitle">Join as a Trekker and start your journey</p>

      <div v-if="error" class="auth-error">{{ error }}</div>

      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label>Username</label>
          <input type="text" class="premium-input" v-model="username"
            placeholder="Choose a username" required autocomplete="username">
        </div>
        <div class="form-group">
          <label>Email Address</label>
          <input type="email" class="premium-input" v-model="email"
            placeholder="your@email.com" required autocomplete="email">
        </div>
        <div class="form-group">
          <label>Password</label>
          <input type="password" class="premium-input" v-model="password"
            placeholder="Create a strong password" required autocomplete="new-password" minlength="6">
        </div>
        <button type="submit" class="btn-premium btn-primary auth-btn" :disabled="loading">
          {{ loading ? 'Creating Account…' : 'Create Account' }}
        </button>
      </form>

      <p class="auth-footer">
        Already have an account? <router-link to="/login">Sign in here</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '../composables/useToast.js'
export default {
  name: 'RegisterView',
  setup() {
    const router = useRouter()
    const { success } = useToast()
    const username = ref(''), email = ref(''), password = ref(''), error = ref(''), loading = ref(false)
    const handleRegister = async () => {
      error.value = ''; loading.value = true
      try {
        const res = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: username.value, email: email.value, password: password.value })
        })
        const data = await res.json()
        if (res.ok) { success('Account created! Please sign in.'); router.push('/login') }
        else { error.value = data.msg || 'Registration failed' }
      } catch { error.value = 'Network error. Please try again.' }
      finally { loading.value = false }
    }
    return { username, email, password, error, loading, handleRegister }
  }
}
</script>
