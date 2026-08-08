/**
 * Shared Chart.js defaults for the TMA dark theme.
 * Import and call applyChartDefaults() once at app startup (main.js),
 * or call it inside each chart component.
 */
import { Chart, defaults } from 'chart.js'

export function applyChartDefaults() {
  defaults.color = '#94a3b8'           // axis labels, legend text
  defaults.borderColor = 'rgba(255,255,255,0.07)'  // grid lines
  defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"
  defaults.font.size = 12

  defaults.plugins.legend.labels.color = '#94a3b8'
  defaults.plugins.legend.labels.padding = 16
  defaults.plugins.legend.labels.usePointStyle = true

  defaults.plugins.tooltip.backgroundColor = 'rgba(15,23,42,0.92)'
  defaults.plugins.tooltip.titleColor = '#f8fafc'
  defaults.plugins.tooltip.bodyColor = '#94a3b8'
  defaults.plugins.tooltip.borderColor = 'rgba(59,130,246,0.4)'
  defaults.plugins.tooltip.borderWidth = 1
  defaults.plugins.tooltip.padding = 10
  defaults.plugins.tooltip.cornerRadius = 8
}

/** Palette consistent with the app's CSS variables */
export const PALETTE = {
  blue:    'rgba(59,  130, 246, 1)',
  green:   'rgba(16,  185, 129, 1)',
  amber:   'rgba(245, 158, 11,  1)',
  red:     'rgba(239, 68,  68,  1)',
  purple:  'rgba(168, 85,  247, 1)',
  cyan:    'rgba(6,   182, 212, 1)',
  pink:    'rgba(236, 72,  153, 1)',
  orange:  'rgba(249, 115, 22,  1)',
}

export const PALETTE_ALPHA = Object.fromEntries(
  Object.entries(PALETTE).map(([k, v]) => [k, v.replace(', 1)', ', 0.18)')])
)

export const PIE_COLORS = Object.values(PALETTE)
export const PIE_COLORS_ALPHA = Object.values(PALETTE_ALPHA)

/** Build a standard scales config for dark-theme cartesian charts */
export function darkScales(opts = {}) {
  return {
    x: {
      grid: { color: 'rgba(255,255,255,0.05)' },
      ticks: { color: '#94a3b8', ...(opts.xTicks || {}) },
      ...(opts.x || {})
    },
    y: {
      grid: { color: 'rgba(255,255,255,0.05)' },
      ticks: { color: '#94a3b8', ...(opts.yTicks || {}) },
      beginAtZero: true,
      ...(opts.y || {})
    }
  }
}
