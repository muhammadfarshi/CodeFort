import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-inter)"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "Liberation Mono", "Courier New", "monospace"],
      },
      colors: {
        severity: {
          info: "#6b7280",
          low: "#3b82f6",
          medium: "#f59e0b",
          high: "#ea580c",
          critical: "#dc2626",
        },
        brand: {
          DEFAULT: "#3b82f6",
        },
        surface: {
          DEFAULT: "#111827",
          elevated: "#1f2937",
        },
        text: {
          primary: "#f9fafb",
          secondary: "#9ca3af",
        },
        border: {
          DEFAULT: "#374151",
        }
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
      },
      borderRadius: {
        card: "12px",
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
};
export default config;
