/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        serif: ["Source Serif 4", "Georgia", "serif"],
        sans: ["IBM Plex Sans", "system-ui", "sans-serif"],
      },
      colors: {
        paper: "#FAF7F0",
        "paper-dim": "#F1ECE1",
        ink: "#2B2621",
        "ink-soft": "#6B6154",
        "ink-faint": "#A69B8A",
        line: "#DDD5C7",
        brass: "#A67C3D",
        "brass-dark": "#8A6530",
        brick: "#A6503D",
        "brick-soft": "#C97D6D",
        sage: "#6E8F6B",
        "sage-soft": "#9BB498",
      },
    },
  },
  plugins: [],
};
