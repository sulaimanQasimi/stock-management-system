import React from 'react';
import { createRoot } from 'react-dom/client';
import { createInertiaApp } from '@inertiajs/react';
import './index.css';

createInertiaApp({
  resolve: async (name) => {
    const pages = import.meta.glob('./Pages/**/*.{jsx,tsx}');
    const importPage = pages[`./Pages/${name}.jsx`] || pages[`./Pages/${name}.tsx`];

    if (!importPage) {
      throw new Error(`Missing Inertia page component: ${name}`);
    }

    const page = await importPage();
    return page.default;
  },
  setup({ el, App, props }) {
    createRoot(el).render(<App {...props} />);
  },
});
