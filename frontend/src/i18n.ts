import { router, usePage } from '@inertiajs/react';

type TranslationPayload = {
  language?: string;
  direction?: 'ltr' | 'rtl';
  translations?: Record<string, string>;
  available?: Array<{ code: string; label: string }>;
};

type PageProps = {
  auth?: {
    i18n?: TranslationPayload;
  };
};

export function useI18n() {
  const { props, url } = usePage<PageProps>();
  const i18n = props.auth?.i18n || {};
  const translations = i18n.translations || {};
  const language = i18n.language || 'en';
  const direction = i18n.direction || 'ltr';
  const available = i18n.available || [
    { code: 'en', label: 'English' },
    { code: 'fa', label: 'دری' },
    { code: 'ps', label: 'پښتو' },
  ];

  function t(key: string, fallback?: string) {
    return translations[key] || fallback || key;
  }

  function setLanguage(nextLanguage: string) {
    const [path, queryString = ''] = url.split('?');
    const params = new URLSearchParams(queryString);
    params.set('lang', nextLanguage);
    router.get(path, Object.fromEntries(params.entries()), { preserveState: false, preserveScroll: true, replace: true });
  }

  return { t, language, direction, available, setLanguage };
}
