import { createInertiaApp } from '@inertiajs/react';
import './styles.css';

createInertiaApp({
  resolve: (name) => {
    const pages = import.meta.glob('./Pages/**/*.{jsx,tsx}', { eager: true });
    const page = pages[`./Pages/${name}.tsx`] || pages[`./Pages/${name}.jsx`];

    if (!page) {
      throw new Error(`Page not found: ${name}`);
    }

    return page.default;
  },
});
