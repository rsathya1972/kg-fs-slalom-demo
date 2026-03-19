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
        slalom: {
          DEFAULT: "#00A3AD",
          50: "#E6F7F8",
          100: "#CCEFF1",
          200: "#99DFE3",
          300: "#66CFD5",
          400: "#33BFC7",
          500: "#00A3AD",
          600: "#008A94",
          700: "#00717A",
          800: "#005861",
          900: "#003F47",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
