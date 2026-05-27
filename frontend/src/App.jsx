import { createInertiaApp } from '@inertiajs/react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const pages = import.meta.glob('./Pages/**/*.{jsx,tsx}');

createInertiaApp({
  resolve: async (name) => {
    const importPage = pages[`./Pages/${name}.tsx`] ?? pages[`./Pages/${name}.jsx`];

    if (!importPage) {
      throw new Error(`Page not found: ${name}`);
    }

    const page = await importPage();
    return page.default;
  },
  setup({ el, App, props }) {
    createRoot(el).render(<App {...props} />);
  },
});
