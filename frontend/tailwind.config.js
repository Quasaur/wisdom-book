/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        topic: "#d53f8c",    // magenta for Topics
        thought: "#38a169",  // green for Thoughts
        quote: "#ecc94b",    // yellow for Quotes
        passage: "#3182ce",  // blue for Passages
      }
    },
  },
  plugins: [],
}
