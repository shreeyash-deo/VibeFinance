/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#090d16',
        surface: '#111827',
        surfaceHover: '#1f2937',
        border: '#1e293b',
        accent: '#3b82f6',
        bullish: '#10b981',
        bearish: '#ef4444',
        neutral: '#6b7280',
        warning: '#f59e0b',
      },
    },
  },
  plugins: [],
}

