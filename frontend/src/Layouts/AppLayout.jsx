import React, { useMemo, useState } from 'react';
import { Link, usePage } from '@inertiajs/react';
import { useI18n } from '../i18n';

const navigation = [
  { key: 'nav.dashboard', href: '/', icon: '◼' },
  { key: 'nav.operations', href: '/operations/', icon: '★' },
  { key: 'nav.productSearch', href: '/product-search/', icon: '⌕' },
  { key: 'nav.products', href: '/products/', icon: '□' },
  { key: 'nav.services', href: '/services/', icon: '◇' },
  { key: 'nav.stockMovements', href: '/stock-movements/', icon: '↕' },
  { key: 'nav.departments', href: '/departments/', icon: '⌂' },
  { key: 'nav.purchases', href: '/purchase-batches/', icon: '+' },
  { key: 'nav.sales', href: '/sales/', icon: '−' },
  { key: 'nav.saleServices', href: '/sale-service-items/', icon: '✦' },
  { key: 'nav.finance', href: '/accounts/', icon: '$' },
  { key: 'nav.reports', href: '/stock-profit-reports/', icon: '↗' },
];

function NavLink({ item, active, onClick, t }) {
  return (
    <Link
      href={item.href}
      onClick={onClick}
      className={[
        'group flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition-all duration-200',
        active
          ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/20'
          : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
      ].join(' ')}
    >
      <span
        className={[
          'flex h-9 w-9 items-center justify-center rounded-xl text-sm transition-colors',
          active ? 'bg-white/15 text-white' : 'bg-slate-100 text-slate-500 group-hover:bg-white',
        ].join(' ')}
      >
        {item.icon}
      </span>
      <span>{t(item.key)}</span>
    </Link>
  );
}

export default function AppLayout({ title, subtitle, titleKey = null, subtitleKey = null, children }) {
  const { url, props } = usePage();
  const { t, language, direction, available, setLanguage } = useI18n();
  const [open, setOpen] = useState(false);

  const user = props?.auth?.user || props?.user;

  const pageTitle = useMemo(
    () => (titleKey ? t(titleKey, title) : title),
    [t, titleKey, title],
  );

  const pageSubtitle = useMemo(
    () => (subtitleKey ? t(subtitleKey, subtitle) : subtitle),
    [t, subtitleKey, subtitle],
  );

  const isActive = (href) =>
    href === '/' ? url === '/' : url.startsWith(href.replace(/\/$/, ''));

  const sidebar = (
    <>
      <div className="mb-8 border-b border-slate-100 pb-6">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-600 text-lg font-black text-white shadow-lg shadow-emerald-600/20">
            S
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-slate-900">
              {t('app.name', 'StockUp')}
            </h1>
            <p className="text-xs text-slate-500">
              {t('app.tagline', 'Inventory command center')}
            </p>
          </div>
        </div>
      </div>

      <nav className="space-y-2" aria-label="Primary navigation">
        {navigation.map((item) => (
          <NavLink
            key={item.href}
            item={item}
            active={isActive(item.href)}
            onClick={() => setOpen(false)}
            t={t}
          />
        ))}
      </nav>

      <div className="mt-8 rounded-3xl border border-slate-200 bg-slate-50/80 p-4 backdrop-blur">
        <div className="mb-4">
          <p className="text-sm font-semibold text-slate-900">
            {user?.username || user?.name || 'StockUp User'}
          </p>
          <p className="text-xs text-slate-500">Active session</p>
        </div>

        <label
          className="block text-xs font-semibold uppercase tracking-wide text-slate-500"
          htmlFor="language-switcher"
        >
          {t('language.label', 'Language')}
        </label>

        <select
          id="language-switcher"
          value={language}
          onChange={(event) => setLanguage(event.target.value)}
          className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 outline-none ring-0 transition focus:border-emerald-500"
        >
          {available.map((item) => (
            <option key={item.code} value={item.code}>
              {item.label}
            </option>
          ))}
        </select>
      </div>
    </>
  );

  return (
    <div dir={direction} className="min-h-screen bg-slate-100 text-slate-900">
      <aside className="fixed inset-y-0 left-0 hidden w-72 overflow-y-auto border-r border-slate-200 bg-white px-5 py-6 lg:block">
        {sidebar}
      </aside>

      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/90 backdrop-blur lg:hidden">
        <div className="flex items-center justify-between px-4 py-4">
          <Link href="/" className="flex items-center gap-3 font-bold text-slate-900">
            <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-emerald-600 text-white shadow-md">
              S
            </span>
            <span>{t('app.name', 'StockUp')}</span>
          </Link>

          <button
            type="button"
            onClick={() => setOpen(true)}
            className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50"
          >
            Menu
          </button>
        </div>
      </header>

      {open ? (
        <div
          className="fixed inset-0 z-40 bg-slate-950/40 backdrop-blur-sm lg:hidden"
          onClick={() => setOpen(false)}
        />
      ) : null}

      <aside
        className={[
          'fixed inset-y-0 left-0 z-50 w-80 max-w-[88vw] overflow-y-auto border-r border-slate-200 bg-white p-6 shadow-2xl transition-transform duration-300 lg:hidden',
          open ? 'translate-x-0' : '-translate-x-full',
        ].join(' ')}
      >
        <div className="mb-4 flex justify-end">
          <button
            type="button"
            onClick={() => setOpen(false)}
            className="rounded-xl px-3 py-2 text-sm font-medium text-slate-500 transition hover:bg-slate-100 hover:text-slate-900"
          >
            Close
          </button>
        </div>

        {sidebar}
      </aside>

      <main className="lg:pl-72">
        <div className="border-b border-slate-200 bg-gradient-to-br from-white to-slate-50 px-4 py-6 sm:px-6">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-3xl font-black tracking-tight text-slate-900">
                {pageTitle}
              </h2>

              {pageSubtitle ? (
                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                  {pageSubtitle}
                </p>
              ) : null}
            </div>
          </div>
        </div>

        <section className="p-4 sm:p-6">{children}</section>
      </main>
    </div>
  );
}
