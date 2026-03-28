/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        obsidian: {
          950: '#020617',
          900: '#111417',
          850: '#191c1f',
          800: '#1d2023',
          700: '#272a2e',
          600: '#323538',
        },
        healthy: '#22c55e',
        atrisk: '#f59e0b',
        critical: '#ef4444',
        primary: {
          50: '#eff6ff', 100: '#dbeafe', 200: '#bfdbfe',
          300: '#93c5fd', 400: '#60a5fa', 500: '#3b82f6',
          600: '#2563eb', 700: '#1d4ed8', 800: '#1e40af', 900: '#1e3a8a',
        },
        cyber: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae0f5',
          300: '#7cc8fb',
          400: '#36b3f8',
          500: '#0ca5f2',
          600: '#028dc9',
          700: '#036fa0',
          800: '#065786',
          900: '#0a4a6d',
          purple: '#8b5cf6',
          purpleDark: '#6d28d9',
          attack: '#dc2626',
          attackGlow: 'rgba(220, 38, 38, 0.5)',
        },
      },
      animation: {
        'pulse-fast': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'attack-pulse': 'attackPulse 2s ease-in-out infinite',
        'glow': 'glow 1.5s ease-in-out infinite alternate',
        'flow-scan': 'flowScan 2.6s linear infinite',
      },
      keyframes: {
        attackPulse: {
          '0%, 100%': {
            opacity: 1,
            transform: 'scale(1)',
            boxShadow: '0 0 0 rgba(220, 38, 38, 0)',
          },
          '50%': {
            opacity: 0.78,
            transform: 'scale(1.05)',
            boxShadow: '0 0 20px rgba(220, 38, 38, 0.6)',
          },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(139, 92, 246, 0.5)' },
          '100%': { boxShadow: '0 0 20px rgba(139, 92, 246, 0.8)' },
        },
        flowScan: {
          '0%': { transform: 'translateX(-120%)', opacity: 0 },
          '20%': { opacity: 0.65 },
          '80%': { opacity: 0.65 },
          '100%': { transform: 'translateX(120%)', opacity: 0 },
        },
      },
    },
  },
  plugins: [],
}
