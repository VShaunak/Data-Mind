/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        google: {
          bg: '#FFFFFF',
          secondary: '#F8F9FA',
          surface: '#F1F3F4',
          surfaceHover: '#E8EAED',
          border: '#DADCE0',
          text: '#202124',
          muted: '#5F6368',
          subtle: '#80868B',
          blue: {
            DEFAULT: '#1A73E8',
            hover: '#1557B0',
            subtle: '#E8F0FE',
            darkSubtle: '#172B4D',
          },
          green: {
            DEFAULT: '#188038',
            subtle: '#E6F4EA',
          },
          red: {
            DEFAULT: '#D93025',
            subtle: '#FCE8E6',
          },
          amber: {
            DEFAULT: '#F29900',
            subtle: '#FEF7E0',
          },
          dark: {
            bg: '#202124',
            secondary: '#292A2D',
            surface: '#303134',
            surfaceHover: '#3C4043',
            border: '#3C4043',
            text: '#E8EAED',
            muted: '#9AA0A6',
            subtle: '#BDC1C6',
          }
        }
      },
      fontFamily: {
        sans: [
          'Google Sans',
          'Inter',
          'Roboto',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'sans-serif'
        ],
        mono: [
          '"JetBrains Mono"',
          '"Roboto Mono"',
          'Consolas',
          'monospace'
        ]
      },
      borderRadius: {
        sm: '6px',
        DEFAULT: '8px',
        md: '10px',
        lg: '12px',
        full: '9999px',
      },
      boxShadow: {
        subtle: '0 1px 2px 0 rgba(60,64,67,0.1), 0 1px 3px 1px rgba(60,64,67,0.06)',
        dropdown: '0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.04)',
        modal: '0 12px 24px -4px rgba(0, 0, 0, 0.12), 0 4px 8px -2px rgba(0, 0, 0, 0.06)',
      },
      transitionDuration: {
        120: '120ms',
        150: '150ms',
        180: '180ms',
        200: '200ms',
        220: '220ms',
      }
    },
  },
  plugins: [],
}

