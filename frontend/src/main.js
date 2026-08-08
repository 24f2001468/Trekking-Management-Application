import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'
import './assets/dashboard-layout.css'

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
