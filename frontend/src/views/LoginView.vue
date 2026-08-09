<template>
  <div class="auth-page">
    <div class="auth-card glass-panel">
      <div class="auth-logo">
        <span class="icon-wrap">🏔️</span>
        <span class="logo-name">TMA</span>
      </div>
      <h2 class="auth-title">Welcome Back</h2>
      <p class="auth-subtitle">Sign in to continue your adventure</p>

      <div v-if="error" class="auth-error">{{ error }}</div>

      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label>Username</label>
          <input type="text" class="premium-input" v-model="username"
            placeholder="Enter your username" required autocomplete="username">
        </div>
        <div class="form-group">
          <label>Password</label>
          <input type="password" class="premium-input" v-model="password"
            placeholder="Enter your password" required autocomplete="current-password">
        </div>
        <button type="submit" class="btn-premium btn-primary auth-btn" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Sign In' }}
        </button>
      </form>

      <p class="auth-footer">
        New here? <router-link to="/register">Create a Trekker account</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '../composables/useToast.js'
export default {
  name: 'LoginView',
  setup() {
    const router = useRouter()
    const { success } = useToast()
    const username = ref(''), password = ref(''), error = ref(''), loading = ref(false)
    const handleLogin = async () => {
      error.value = ''; loading.value = true
      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: username.value, password: password.value })
        })
        const data = await res.json()
        if (res.ok) {
          localStorage.setItem('tma_token', data.access_token)
          localStorage.setItem('tma_user', JSON.stringify(data.user))
          success(`Welcome back, ${data.user.username}!`)
          if (data.user.role === 'Admin') router.replace('/admin')
          else if (data.user.role === 'Trek Staff') router.replace('/staff')
          else router.replace('/trekker')
        } else { error.value = data.msg || 'Login failed' }
      } catch { error.value = 'Network error. Please try again.' }
      finally { loading.value = false }
    }
    return { username, password, error, loading, handleLogin }
  }
}
</script>
