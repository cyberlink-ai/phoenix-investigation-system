/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Placeholder investigation-console palette - to be revisited and
        // deliberately designed (not left as defaults) during the dedicated
        // UI/dashboard build phase, per frontend-design guidance.
        console: {
          bg: "#0B0F14",
          panel: "#121821",
          line: "#1E2733",
          text: "#E6EDF3",
          muted: "#8B98A5",
          accent: "#3DDC97",
          warn: "#E0A93D",
          alert: "#E05D3D",
        },
      },
    },
  },
  plugins: [],
};
