import { createRouter, createWebHistory } from 'vue-router'

import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import StaffDashboard from '../views/StaffDashboard.vue'
import TrekkerDashboard from '../views/TrekkerDashboard.vue'

import AdminHome from '../components/admin/AdminHome.vue'
import AdminTreks from '../components/admin/AdminTreks.vue'
import AdminUsers from '../components/admin/AdminUsers.vue'
import AdminStaff from '../components/admin/AdminStaff.vue'
import AdminBookings from '../components/admin/AdminBookings.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: LoginView },
  { path: '/register', name: 'Register', component: RegisterView },
  { 
    path: '/admin', 
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'Admin' },
    children: [
      { path: '', name: 'AdminHome', component: AdminHome },
      { path: 'treks', name: 'AdminTreks', component: AdminTreks },
      { path: 'users', name: 'AdminUsers', component: AdminUsers },
      { path: 'staff', name: 'AdminStaff', component: AdminStaff },
      { path: 'bookings', name: 'AdminBookings', component: AdminBookings }
    ]
  },
  { 
    path: '/staff', 
    name: 'StaffDashboard', 
    component: StaffDashboard,
    meta: { requiresAuth: true, role: 'Trek Staff' }
  },
  { 
    path: '/trekker', 
    name: 'TrekkerDashboard', 
    component: TrekkerDashboard,
    meta: { requiresAuth: true, role: 'Trekker' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation Guard for Role-Based Access Control
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('tma_token');
  const userStr = localStorage.getItem('tma_user');
  let user = null;
  
  if (userStr) {
    try {
      user = JSON.parse(userStr);
    } catch (e) {
      console.error('Error parsing user data');
    }
  }

  // If route requires authentication
  if (to.meta.requiresAuth) {
    if (!token || !user) {
      return next('/login');
    }
    // Check if user has the correct role
    if (to.meta.role && to.meta.role !== user.role) {
      // Redirect to their respective dashboard if they try to access wrong role dashboard
      if (user.role === 'Admin') return next('/admin');
      if (user.role === 'Trek Staff') return next('/staff');
      if (user.role === 'Trekker') return next('/trekker');
      return next('/login');
    }
  }
  
  // If user is already logged in and tries to access login/register
  if ((to.path === '/login' || to.path === '/register') && token && user) {
      if (user.role === 'Admin') return next('/admin');
      if (user.role === 'Trek Staff') return next('/staff');
      if (user.role === 'Trekker') return next('/trekker');
  }

  next();
})

export default router
