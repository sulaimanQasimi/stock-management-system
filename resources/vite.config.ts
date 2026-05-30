import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import inertia from '@inertiajs/vite';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  plugins: [
    react(),
    inertia(),
  ],
  resolve: {
    alias: {
      'tailwindcss/version.js': fileURLToPath(new URL('./js/tailwind-version-shim.js', import.meta.url)),
    },
  },
  build: {
    manifest: true,
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: 'js/main.tsx',
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
});
