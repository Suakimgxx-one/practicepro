/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Plus Jakarta Sans", "system-ui", "sans-serif"],
      },
      colors: {
        surface: {
          950: "#0A0B10",
          900: "#111219",
          800: "#191B24",
          700: "#242631",
        },
        border: {
          subtle: "#242631",
          DEFAULT: "#2E313F",
        },
        ink: {
          100: "#F3F4F7",
          300: "#C4C6D3",
          500: "#8B8FA3",
          700: "#5A5D6E",
        },
        accent: {
          400: "#9C8CFF",
          500: "#7C6CF6",
          600: "#6353E0",
          glow: "#7C6CF64D",
        },
        success: "#34D399",
        warning: "#FBBF24",
        danger: "#F87171",
      },
      boxShadow: {
        glow: "0 0 40px -8px rgba(124, 108, 246, 0.35)",
        panel: "0 8px 30px -12px rgba(0, 0, 0, 0.6)",
      },
    },
  },
  plugins: [],
};
