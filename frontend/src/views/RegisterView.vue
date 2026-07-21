<template>
  <div class="row justify-content-center">
    <div class="col-md-6">
      <div class="card mt-5">
        <div class="card-header">
          <h3 class="mb-0">Trekker Registration</h3>
        </div>
        <div class="card-body">
          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          <div v-if="success" class="alert alert-success">{{ success }}</div>
          <form @submit.prevent="handleRegister">
            <div class="mb-3">
              <label class="form-label">Username</label>
              <input type="text" class="form-control" v-model="username" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Email address</label>
              <input type="email" class="form-control" v-model="email" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Password</label>
              <input type="password" class="form-control" v-model="password" required>
            </div>
            <button type="submit" class="btn btn-success w-100">Register</button>
          </form>
          <div class="mt-3 text-center">
            <router-link to="/login">Already have an account? Login here</router-link>
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
      email: '',
      password: '',
      error: '',
      success: ''
    }
  },
  methods: {
    async handleRegister() {
      this.error = '';
      this.success = '';
      try {
        const response = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            username: this.username, 
            email: this.email,
            password: this.password 
          })
        });
        
        const data = await response.json();
        
        if (response.ok) {
          this.success = 'Registration successful! You can now login.';
          this.username = '';
          this.email = '';
          this.password = '';
        } else {
          this.error = data.msg || 'Registration failed';
        }
      } catch (err) {
        this.error = 'Network error occurred';
      }
    }
  }
}
</script>
