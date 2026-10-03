/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts}", "./public/**/*.html"],
  theme: {
    extend: {
      colors: {
        gray: {
          100: "#f3f4f6",
          800: "#1f2937",
          900: "#111827",
        },
        severity: {
          info: "#6b7280",
          low: "#f59e0b",
          medium: "#d97706",
          high: "#ef4444",
          critical: "#991b1b"
        }
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "monospace"],
      },
      spacing: {
        '4': '4px',
        '8': '8px',
        '12': '12px',
        '16': '16px',
        '24': '24px',
        '32': '32px',
        '48': '48px',
        '64': '64px',
      }
    },
  },
  plugins: [],
}
