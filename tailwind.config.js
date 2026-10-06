/** Konfigurasi Tailwind (di-build statis, bukan runtime JIT) — TEMA "AURORA GLASS" */
module.exports = {
  darkMode: 'class',
  content: [
    "./index.html",
    "./blog/**/*.html",
    "./*.html",
    "./js/**/*.js"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        primary:   '#7c5cff',   // aksen ungu
        secondary: '#3b82f6',   // aksen biru
        accent:    '#ffb020',   // CTA amber
        dark:      '#0b1226',
        darker:    '#070b18',
        card:      '#111936',
        line:      '#232c4d',
        ink:       '#eef2ff'
      },
      boxShadow: {
        glow: '0 18px 40px -18px rgba(124,92,255,.65)',
        cta:  '0 10px 26px -12px rgba(255,138,0,.75)'
      }
    }
  },
  plugins: [],
}
