import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: { // Your existing server proxy if you have one
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  test: { // Add this test configuration block
    globals: true, // Allows using Vitest globals (describe, it, expect) without importing
    environment: 'jsdom', // Use JSDOM for testing React components
    setupFiles: './src/setupTests.js', // Optional: a setup file for global test configurations
    css: true, // If you need to process CSS imports in tests (e.g., CSS Modules)
  },
})
