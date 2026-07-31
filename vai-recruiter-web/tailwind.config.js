/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: '#123d35',
        'forest-2': '#1c5549',
        mint: '#bfe8d5',
        cream: '#f4f2e9',
        paper: '#fffef9',
        ink: '#1e2926',
        muted: '#6f7975',
        line: '#dedfd7',
        amber: '#c98224',
        red: '#b85141',
      },
      fontFamily: {
        serif: ['Fraunces', 'serif'],
        mono: ['JetBrains Mono', 'monospace'],
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
