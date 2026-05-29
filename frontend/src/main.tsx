import { createInertiaApp } from '@inertiajs/react';
import { createRoot } from 'react-dom/client';
import './index.css';

type PageModule = {
  default: React.ComponentType<Record<string, unknown>>;
};

const pages = import.meta.glob<PageModule>('./Pages/**/*.{jsx,tsx}');

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
  title: (title) => (title ? `${title} - Stock Management System` : 'Stock Management System'),
  resolve: resolvePage,
  setup({ el, App, props }) {
    createRoot(el).render(<App {...props} />);
  },
});
