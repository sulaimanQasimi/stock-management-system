import React from 'react';
import { createInertiaApp } from '@inertiajs/react';
import { createRoot } from 'react-dom/client';
import './index.css';

const pages = import.meta.glob('./Pages/**/*.{jsx,tsx}');

function readInitialPage() {
  const el = document.getElementById('app');

  if (!el) {
    throw new Error('Inertia root element #app was not found.');
  }

  const rawPage = el.getAttribute('data-page');

  if (!rawPage) {
    throw new Error('Missing Inertia data-page payload on #app.');
  }

  const page = JSON.parse(rawPage);

  if (!page || !page.component) {
    throw new Error('Invalid Inertia page payload on #app.');
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
  title: (title) => (title ? title + ' - Stock Management System' : 'Stock Management System'),
  resolve: resolvePage,
  setup({ el, App, props }) {
    createRoot(el).render(React.createElement(App, props));
  },
});
