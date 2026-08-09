import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'
import '@/assets/custom.css'
// import './assets/dashboard-layout.css' // removed per Bootstrap‑only styling plan

// Register all Chart.js components globally
import {
  Chart,
  CategoryScale, LinearScale, BarElement, LineElement, PointElement,
  ArcElement, Title, Tooltip, Legend, Filler
} from 'chart.js'
import { applyChartDefaults } from './composables/useChartDefaults.js'

Chart.register(
  CategoryScale, LinearScale, BarElement, LineElement, PointElement,
  ArcElement, Title, Tooltip, Legend, Filler
)
applyChartDefaults()

const app = createApp(App)

app.use(router)

app.mount('#app')

// Clear caches and unregister service workers on load to avoid stale assets
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(regs => {
    for (const reg of regs) {
      reg.unregister()
    }
  })
}
if ('caches' in window) {
  caches.keys().then(keys => {
    for (const key of keys) {
      caches.delete(key)
    }
  })
}
