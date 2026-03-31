/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#0a0e1a',
          800: '#0f1629',
          700: '#141c35',
          600: '#1a2342',
          500: '#1e2a4a',
          400: '#243055',
        },
        accent: {
          blue:  '#3b82f6',
          green: '#10b981',
          red:   '#ef4444',
          gold:  '#f59e0b',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
}
