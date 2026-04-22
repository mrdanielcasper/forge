import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8000'
    }
  },
  // ADD THIS BLOCK: Tell Vitest to only run tests in the web folder
  test: {
    include: ['tests/web/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    environment: 'happy-dom' // standard for React component testing
  }
});