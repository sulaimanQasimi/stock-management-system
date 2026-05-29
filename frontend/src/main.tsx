import React from 'react';
import { createInertiaApp } from '@inertiajs/react';
import { createRoot } from 'react-dom/client';
import './index.css';

type PageModule = {
  default: React.ComponentType<Record<string, unknown>>;
};

type InertiaPage = {
  component: string;
  props: Record<string, unknown>;
  url: string;
  version: string | null;
};

const pages = import.meta.glob<PageModule>('./Pages/**/*.{jsx,tsx}');

const readInitialPage = (): InertiaPage => {
  const el = document.getElementById('app');
  const rawPage = el?.getAttribute('data-page');

  if (!el) {
    throw new Error('Inertia root element #app was not found.');
  }

  if (!rawPage) {
    throw new Error('Missing Inertia data-page payload on #app.');
  }

  const page = JSON.parse(rawPage) as InertiaPage | null;

  if (!page?.component) {
    throw new Error(`Invalid Inertia page payload: ${rawPage}`);
  }

  return page;
};

const resolvePage = async (name: string) => {
  const candidates = [
    `./Pages/${name}.tsx`,
    `./Pages/${name}.jsx`,
    `./Pages/${name}/Index.tsx`,
    `./Pages/${name}/Index.jsx`,
    `./Pages/${name}/index.tsx`,
    `./Pages/${name}/index.jsx`,
  ];

  const importPage = candidates.map((path) => pages[path]).find(Boolean);

  if (!importPage) {
    throw new Error(
      `Missing Inertia page component "${name}". Expected one of: ${candidates.join(', ')}`,
    );
  }

  const page = await importPage();
  return page.default;
};

createInertiaApp({
  id: 'app',
  page: readInitialPage(),
  title: (title) => (title ? `${title} - Stock Management System` : 'Stock Management System'),
  resolve: resolvePage,
  setup({ el, App, props }) {
    createRoot(el).render(<App {...props} />);
  },
});
