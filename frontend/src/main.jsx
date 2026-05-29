import '@vitejs/plugin-react/preamble';
import React from 'react';
import { createRoot } from 'react-dom/client';
import { createInertiaApp } from '@inertiajs/react';
import './index.css';

createInertiaApp({
  initialPage: window.initialPage,
  resolve: (name) => {
    const pages = import.meta.glob('./Pages/**/*.{jsx,tsx}', { eager: true });
    const page = pages[`./Pages/${name}.jsx`] || pages[`./Pages/${name}.tsx`];

    if (!page) {
      throw new Error(`Missing Inertia page component: ${name}`);
    }

    return page;
  },
  setup({ el, App, props }) {
    createRoot(el).render(<App {...props} />);
  },
});
