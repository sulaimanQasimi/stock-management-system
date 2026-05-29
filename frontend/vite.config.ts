import { defineConfig } from 'vite';
import inertia from '@inertiajs/vite';

export default defineConfig({
  plugins: [inertia()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:8000'
    }
  },
  esbuild: {
    jsx: 'automatic',
  },
});
