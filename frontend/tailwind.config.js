/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        netai: {
          bg:       '#0a0e1a',
          surface:  '#111627',
          border:   '#1e2640',
          accent:   '#3b82f6',
          accent2:  '#6366f1',
          tool:     '#f59e0b',
          success:  '#22c55e',
          error:    '#ef4444',
          muted:    '#64748b',
          text:     '#e2e8f0',
          dim:      '#94a3b8',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
