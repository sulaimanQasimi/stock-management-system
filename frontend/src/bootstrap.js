import React from 'react';
import { createRoot } from 'react-dom/client';
import { createInertiaApp } from '@inertiajs/react';
import './index.css';

const appElement = document.getElementById('app');
const domPage = appElement?.dataset?.page ? JSON.parse(appElement.dataset.page) : null;
const initialPage = window.initialPage || domPage;

if (!initialPage || !initialPage.component) {
  throw new Error('Missing Inertia initial page payload.');
}

createInertiaApp({
  page: initialPage,
  resolve: (name) => {
    const pages = import.meta.glob('./Pages/**/*.{jsx,tsx}', { eager: true });
    const page = pages[`./Pages/${name}.jsx`] || pages[`./Pages/${name}.tsx`];
    if (!page) {
      throw new Error(`Missing Inertia page component: ${name}`);
    }
    return page;
  },
  setup({ el, App, props }) {
    createRoot(el).render(React.createElement(App, props));
  },
});
