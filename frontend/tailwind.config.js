/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary-bg': '#202124',
        'content-bg': '#1c2436',
        'sidebar-bg': '#2d2e31',
        'card-bg': '#303134',
        'text-primary': '#e8eaed',
        'text-secondary': '#9aa0a6',
        'accent': '#8ab4f8',
        'accent-bg': '#3c4043',
        'border-color': '#3c4043',
        topic: "#d53f8c",
        thought: "#38a169",
        quote: "#ecc94b",
        passage: "#3182ce",
      },
      spacing: {
        'sidebar-expanded': '280px',
        'sidebar-collapsed': '72px',
        'header-height': '64px',
      },
      fontFamily: {
        sans: ['Google Sans', 'Roboto', 'sans-serif'],
      },
      transitionDuration: {
        '300': '300ms',
      }
    },
  },
  plugins: [],
}
