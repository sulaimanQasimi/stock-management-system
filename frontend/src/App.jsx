import React from 'react';
import { createRoot } from 'react-dom/client';
import { createInertiaApp } from '@inertiajs/react';
import './styles.css';

const jsxPages = import.meta.glob('./Pages/**/*.jsx', { eager: true });
const tsxPages = import.meta.glob('./Pages/**/*.tsx', { eager: true });
const pages = { ...jsxPages, ...tsxPages };

createInertiaApp({
  resolve: (name) => {
    const page = pages[`./Pages/${name}.tsx`] || pages[`./Pages/${name}.jsx`];
    if (!page) {
      throw new Error(`Page not found: ${name}`);
    }
    return page.default;
  },
  setup({ el, App, props }) {
    createRoot(el).render(<App {...props} />);
  },
});
