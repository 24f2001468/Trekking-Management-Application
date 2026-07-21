<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
      <router-link class="navbar-brand" to="/">TMA</router-link>
      <div class="collapse navbar-collapse">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item" v-if="!isAuthenticated">
            <router-link class="nav-link" to="/login">Login</router-link>
          </li>
          <li class="nav-item" v-if="!isAuthenticated">
            <router-link class="nav-link" to="/register">Register</router-link>
          </li>
          <li class="nav-item" v-if="isAuthenticated">
            <button class="btn btn-link nav-link" @click="logout">Logout</button>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <div class="container mt-4">
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App',
  computed: {
    isAuthenticated() {
      // Check if token exists, triggering reactivity on change
      return !!localStorage.getItem('tma_token');
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('tma_token');
      localStorage.removeItem('tma_user');
      this.$router.push('/login');
    }
  }
}
</script>

<style>
/* Global styles can go here */
</style>
