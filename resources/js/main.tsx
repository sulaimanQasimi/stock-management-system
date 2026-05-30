import React from 'react';
import { createInertiaApp } from '@inertiajs/react';
import { createRoot } from 'react-dom/client';
import './index.css';

const pages = import.meta.glob<{ default: React.ComponentType }>(
  './Pages/**/*.{jsx,tsx}',
);

function readInitialPage() {
  const pageElement = document.getElementById('inertia-page');

  if (!pageElement) {
    throw new Error('Missing inertia-page script element.');
  }

  const page = JSON.parse(pageElement.textContent || '{}');

  if (!page || !page.component) {
    throw new Error('Invalid Inertia page payload.');
  }

  return page;
}

async function resolvePage(name) {
  const candidates = [
    './Pages/' + name + '.tsx',
    './Pages/' + name + '.jsx',
    './Pages/' + name + '/Index.tsx',
    './Pages/' + name + '/Index.jsx',
    './Pages/' + name + '/index.tsx',
    './Pages/' + name + '/index.jsx',
  ];

  const importPage = candidates.map((path) => pages[path]).find(Boolean);

  if (!importPage) {
    throw new Error('Missing Inertia page component: ' + name);
  }

  const page = await importPage();
  return page.default || page;
}

createInertiaApp({
  id: 'app',
  page: readInitialPage(),
  resolve: resolvePage,
  setup({ el, App, props }) {
    createRoot(el).render(React.createElement(App, props));
  },
});
