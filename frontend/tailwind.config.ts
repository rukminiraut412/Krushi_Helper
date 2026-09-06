import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          50: "#f0fdf4",
          100: "#dcfce7",
          200: "#bbf7d0",
          300: "#86efac",
          400: "#4ade80",
          500: "#22c55e",
          600: "#16a34a",
          700: "#15803d",
          800: "#166534",
          900: "#14532d",
          950: "#052e16",
        },
        earth: {
          50: "#fbf8f3",
          100: "#f4ede3",
          200: "#e9dac6",
          300: "#dac0a3",
          400: "#c7a17d",
          500: "#b9885e",
          600: "#aa7350",
          700: "#8e5d42",
          800: "#744c3a",
          900: "#604033",
        },
      },
    },
  },
  plugins: [],
};

export default config;
