import { createRouter, createWebHistory } from 'vue-router'

import LandingView    from '../views/LandingView.vue'
import LoginView      from '../views/LoginView.vue'
import RegisterView   from '../views/RegisterView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import StaffDashboard from '../views/StaffDashboard.vue'
import TrekkerDashboard from '../views/TrekkerDashboard.vue'

import AdminHome      from '../components/admin/AdminHome.vue'
import AdminTreks     from '../components/admin/AdminTreks.vue'
import AdminUsers     from '../components/admin/AdminUsers.vue'
import AdminStaff     from '../components/admin/AdminStaff.vue'
import AdminBookings  from '../components/admin/AdminBookings.vue'
import AdminAnalytics from '../components/admin/AdminAnalytics.vue'
import PaymentOverview from '../components/PaymentOverview.vue'
import TrekSearch      from '../components/TrekSearch.vue'

import StaffHome        from '../components/staff/StaffHome.vue'
import StaffTreks       from '../components/staff/StaffTreks.vue'
import StaffTrekDetails from '../components/staff/StaffTrekDetails.vue'

import TrekkerHome     from '../components/trekker/TrekkerHome.vue'
import TrekkerBrowse   from '../components/trekker/TrekkerBrowse.vue'
import TrekkerBookings from '../components/trekker/TrekkerBookings.vue'
import TrekkerHistory  from '../components/trekker/TrekkerHistory.vue'
import TrekkerProfile  from '../components/trekker/TrekkerProfile.vue'

const routes = [
  { path: '/', name: 'Landing', component: LandingView },
  { path: '/login',    name: 'Login',    component: LoginView },
  { path: '/register', name: 'Register', component: RegisterView },

  {
    path: '/admin',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'Admin' },
    children: [
      { path: '',            name: 'AdminHome',      component: AdminHome },
      { path: 'treks',       name: 'AdminTreks',     component: AdminTreks },
      { path: 'users',       name: 'AdminUsers',     component: AdminUsers },
      { path: 'staff',       name: 'AdminStaff',     component: AdminStaff },
      { path: 'bookings',    name: 'AdminBookings',  component: AdminBookings },
      { path: 'payments',    name: 'AdminPayments',  component: PaymentOverview },
      { path: 'trek-search', name: 'AdminTrekSearch',component: TrekSearch },
      { path: 'analytics',   name: 'AdminAnalytics', component: AdminAnalytics }
    ]
  },

  {
    path: '/staff',
    component: StaffDashboard,
    meta: { requiresAuth: true, role: 'Trek Staff' },
    children: [
      { path: '',           name: 'StaffHome',        component: StaffHome },
      { path: 'treks',      name: 'StaffTreks',       component: StaffTreks },
      { path: 'treks/:id',  name: 'StaffTrekDetails', component: StaffTrekDetails }
    ]
  },

  {
    path: '/trekker',
    component: TrekkerDashboard,
    meta: { requiresAuth: true, role: 'Trekker' },
    children: [
      { path: '',         name: 'TrekkerHome',     component: TrekkerHome },
      { path: 'browse',   name: 'TrekkerBrowse',   component: TrekkerBrowse },
      { path: 'bookings', name: 'TrekkerBookings', component: TrekkerBookings },
      { path: 'history',  name: 'TrekkerHistory',  component: TrekkerHistory },
      { path: 'profile',  name: 'TrekkerProfile',  component: TrekkerProfile }
    ]
  }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const token   = localStorage.getItem('tma_token')
  const userStr = localStorage.getItem('tma_user')
  let user = null
  if (userStr) { try { user = JSON.parse(userStr) } catch (e) {} }

  if (to.meta.requiresAuth) {
    if (!token || !user) return next('/login')
    if (to.meta.role && to.meta.role !== user.role) {
      if (user.role === 'Admin')      return next('/admin')
      if (user.role === 'Trek Staff') return next('/staff')
      if (user.role === 'Trekker')    return next('/trekker')
      return next('/login')
    }
  }

  if ((to.path === '/login' || to.path === '/register') && token && user) {
    if (user.role === 'Admin')      return next('/admin')
    if (user.role === 'Trek Staff') return next('/staff')
    if (user.role === 'Trekker')    return next('/trekker')
  }

  next()
})

export default router
