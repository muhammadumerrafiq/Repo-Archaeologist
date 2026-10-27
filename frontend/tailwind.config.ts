import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          0: 'var(--bg-0)',
          1: 'var(--bg-1)',
          2: 'var(--bg-2)',
        },
        line: {
          DEFAULT: 'var(--line)',
          strong: 'var(--line-strong)',
        },
        text: {
          0: 'var(--text-0)',
          1: 'var(--text-1)',
          2: 'var(--text-2)',
        },
        cyan: {
          DEFAULT: 'var(--cyan)',
        },
        violet: {
          DEFAULT: 'var(--violet)',
        },
        amber: {
          DEFAULT: 'var(--amber)',
        },
        red: {
          DEFAULT: 'var(--red)',
        },
      },
      fontFamily: {
        sans: ['Geist Sans', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '4px',
        sm: '2px',
        md: '4px',
        lg: '6px',
      },
    },
  },
  plugins: [],
};

export default config;
