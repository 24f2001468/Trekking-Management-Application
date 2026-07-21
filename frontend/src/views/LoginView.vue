<template>
  <div class="row justify-content-center">
    <div class="col-md-6">
      <div class="card mt-5">
        <div class="card-header">
          <h3 class="mb-0">Login</h3>
        </div>
        <div class="card-body">
          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          <form @submit.prevent="handleLogin">
            <div class="mb-3">
              <label class="form-label">Username</label>
              <input type="text" class="form-control" v-model="username" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Password</label>
              <input type="password" class="form-control" v-model="password" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">Login</button>
          </form>
          <div class="mt-3 text-center">
            <router-link to="/register">Need an account? Register here (Trekkers only)</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: '',
      password: '',
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      try {
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: this.username, password: this.password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
          localStorage.setItem('tma_token', data.access_token);
          localStorage.setItem('tma_user', JSON.stringify(data.user));
          
          if (data.user.role === 'Admin') this.$router.push('/admin');
          else if (data.user.role === 'Trek Staff') this.$router.push('/staff');
          else this.$router.push('/trekker');
        } else {
          this.error = data.msg || 'Login failed';
        }
      } catch (err) {
        this.error = 'Network error occurred';
      }
    }
  }
}
</script>
