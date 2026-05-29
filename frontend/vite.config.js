import { defineConfig } from 'vite';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  plugins: [],
  resolve: {
    alias: {
      'tailwindcss/version.js': fileURLToPath(new URL('./src/tailwind-version-shim.js', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  esbuild: {
    jsx: 'automatic',
  },
});
