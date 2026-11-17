/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        navy: {
          950: "#070A11",
          900: "#0B0F19",
          850: "#0E1424",
          800: "#111827",
          750: "#162035",
          700: "#1E293B",
          600: "#334155",
          500: "#475569",
        },
        brand: {
          blue: "#0284C7",
          cyan: "#38BDF8",
          emerald: "#10B981",
          rose: "#F43F5E",
          amber: "#F59E0B",
          indigo: "#6366F1",
        }
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "Courier New", "monospace"],
      }
    },
  },
  plugins: [],
}

