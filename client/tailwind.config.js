/** @type {import('tailwindcss').Config} */
const plugin = require('tailwindcss/plugin');

module.exports = {
  theme: {
    extend: {
      backgroundSize: {
        'size-200': '200% 200%',
      },
      backgroundPosition: {
        'pos-0': '0% 0%',
        'pos-100': '100% 100%',
      },
      animation: {
        'siri-throb': 'siriThrob 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'siri-ring': 'siriRing 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'siri-glow': 'siriGlow 2s ease-in-out infinite',
        'siri-wave': 'siriWave 1.5s ease-in-out infinite',
        'siri-pulse': 'siriPulse 1.5s ease-in-out infinite',
        'user-glow': 'userGlow 2s ease-in-out infinite',
      },
      keyframes: {
        siriThrob: {
          '0%, 100%': {
            transform: 'scale(1)',
            opacity: '0.3'
          },
          '50%': {
            transform: 'scale(1.1)',
            opacity: '0.5'
          }
        },
        siriRing: {
          '0%': {
            transform: 'scale(1)',
            opacity: '0.4'
          },
          '100%': {
            transform: 'scale(2)',
            opacity: '0'
          }
        },
        siriGlow: {
          '0%, 100%': {
            opacity: '0.5',
            filter: 'brightness(1)'
          },
          '50%': {
            opacity: '0.8',
            filter: 'brightness(1.2)'
          }
        },
        siriWave: {
          '0%, 100%': {
            transform: 'scale(1)',
            opacity: '0.4'
          },
          '50%': {
            transform: 'scale(1.1)',
            opacity: '0.8'
          }
        },
        siriPulse: {
          '0%, 100%': {
            transform: 'scale(0.95)',
            opacity: '0.5'
          },
          '50%': {
            transform: 'scale(1.05)',
            opacity: '0.8'
          }
        },
        userGlow: {
          '0%, 100%': {
            boxShadow: '0 0 15px 2px rgba(129, 140, 248, 0.4)',
            transform: 'scale(1)'
          },
          '50%': {
            boxShadow: '0 0 20px 4px rgba(129, 140, 248, 0.6)',
            transform: 'scale(1.02)'
          }
        },
      },
    },
  },
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
      },
    },
  },
  plugins: [
    plugin(function({ addUtilities }) {
      addUtilities({
        '.siri-effect': {
          'background': 'radial-gradient(circle, rgba(59, 130, 246, 0.5) 0%, rgba(59, 130, 246, 0) 70%)',
        },
        '.user-effect': {
          'background': 'radial-gradient(circle, rgba(99, 102, 241, 0.5) 0%, rgba(99, 102, 241, 0) 70%)',
        }
      })
    })
  ],
}
