import React from 'react';
import { createRoot } from 'react-dom/client';
import { createInertiaApp } from '@inertiajs/react';
import './index.css';

const appElement = document.getElementById('app');
let initialPage = window.initialPage;

if (typeof initialPage === 'string') {
  initialPage = JSON.parse(initialPage);
}

if (!initialPage && appElement && appElement.dataset && appElement.dataset.page) {
  initialPage = JSON.parse(appElement.dataset.page);
}

if (!appElement || !initialPage || !initialPage.component) {
  throw new Error('Missing Inertia initial page payload. Check templates/app.html page_json rendering.');
}

createInertiaApp({
  initialPage,
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
