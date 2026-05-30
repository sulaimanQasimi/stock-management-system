import React, { useMemo, useState } from 'react';
import { Link, usePage } from '@inertiajs/react';
import { useI18n } from '../i18n';

const navigation = [
  { key: 'nav.dashboard', href: '/', icon: 'dashboard', fallback: 'Dashboard' },
  { key: 'nav.operations', href: '/operations/', icon: 'workflow', fallback: 'Operations' },
  { key: 'nav.productSearch', href: '/product-search/', icon: 'search', fallback: 'Search' },
  { key: 'nav.products', href: '/products/', icon: 'box', fallback: 'Products' },
  { key: 'nav.services', href: '/services/', icon: 'service', fallback: 'Services' },
  { key: 'nav.stockMovements', href: '/stock-movements/', icon: 'transfer', fallback: 'Movements' },
  { key: 'nav.departments', href: '/departments/', icon: 'building', fallback: 'Departments' },
  { key: 'nav.purchases', href: '/purchase-batches/', icon: 'cart', fallback: 'Purchases' },
  { key: 'nav.sales', href: '/sales/', icon: 'receipt', fallback: 'Sales' },
  { key: 'nav.saleServices', href: '/sale-service-items/', icon: 'layers', fallback: 'Sale Services' },
  { key: 'nav.finance', href: '/accounts/', icon: 'wallet', fallback: 'Finance' },
  { key: 'nav.reports', href: '/stock-profit-reports/', icon: 'chart', fallback: 'Reports' },
  { key: 'nav.profile', href: '/profile/', icon: 'user', fallback: 'Profile' },
];

const iconPaths = {
  dashboard: 'M3 13h8V3H3v10Zm0 8h8v-6H3v6Zm10 0h8V11h-8v10Zm0-18v6h8V3h-8Z',
  workflow: 'M6 6h6v4H6V6Zm6 2h4a4 4 0 0 1 4 4v1M6 18h6v-4H6v4Zm6-2h4a4 4 0 0 0 4-4v-1',
  search: 'm20 20-4.5-4.5M10.5 18a7.5 7.5 0 1 1 0-15 7.5 7.5 0 0 1 0 15Z',
  box: 'M21 8.5 12 3 3 8.5m18 0-9 5.5m9-5.5v7L12 21m0-7L3 8.5m9 5.5v7M3 8.5v7L12 21',
  service: 'M12 3v4m0 10v4M4.2 6.2l2.8 2.8m10 10 2.8-2.8M3 12h4m10 0h4M4.2 17.8 7 15m10-10 2.8 2.8M9 12a3 3 0 1 0 6 0 3 3 0 0 0-6 0Z',
  transfer: 'M7 7h14m0 0-4-4m4 4-4 4M17 17H3m0 0 4 4m-4-4 4-4',
  building: 'M4 21V5a2 2 0 0 1 2-2h8v18M4 21h16M8 7h2m-2 4h2m-2 4h2m6-6h4v12m-4-8h2m-2 4h2',
  cart: 'M3 4h2l2.2 11.2A2 2 0 0 0 9.2 17H18a2 2 0 0 0 1.9-1.4L22 8H6m3 13h.01M18 21h.01',
  receipt: 'M6 3h12v18l-3-2-3 2-3-2-3 2V3Zm4 5h8M10 12h8M10 16h5',
  layers: 'm12 3 9 5-9 5-9-5 9-5Zm-7 9 7 4 7-4M5 16l7 4 7-4',
  wallet: 'M4 7a3 3 0 0 1 3-3h11v4H7a3 3 0 0 0 0 6h14v6H7a3 3 0 0 1-3-3V7Zm14 7h3v-4h-3a2 2 0 0 0 0 4Z',
  chart: 'M4 19V5m0 14h16M8 16v-5m4 5V8m4 8v-9',
  user: 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm8 9a8 8 0 1 0-16 0',
  menu: 'M4 7h16M4 12h16M4 17h16',
};

function Icon({ name, className = '' }) {
  return (
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
      className={className}
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d={iconPaths[name]} />
    </svg>
  );
}

function NavLink({ item, active, onClick, t, isRtl }) {
  return (
    <Link
      href={item.href}
      onClick={onClick}
      className={[
        'group relative flex min-h-11 items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-semibold transition-all duration-200',
        isRtl ? 'flex-row-reverse text-right' : 'text-left',
        active
          ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-700/20'
          : 'text-slate-600 hover:bg-slate-100 hover:text-slate-950',
      ].join(' ')}
    >
      <span
        className={[
          'grid h-8 w-8 shrink-0 place-items-center rounded-lg text-xs font-black',
          active ? 'bg-white/15 text-white' : 'bg-white text-slate-500 shadow-sm ring-1 ring-slate-200 group-hover:text-emerald-700',
        ].join(' ')}
      >
        <Icon name={item.icon} className="h-4 w-4" />
      </span>
      <span className="min-w-0 flex-1 truncate">{t(item.key, item.fallback)}</span>
    </Link>
  );
}

function Sidebar({ t, language, available, setLanguage, user, isActive, isRtl, onNavigate }) {
  return (
    <div className="flex h-full flex-col border-slate-200 bg-white/95 shadow-xl shadow-slate-200/70 backdrop-blur">
      <div className="border-b border-slate-100 px-5 py-5">
        <Link href="/" onClick={onNavigate} className="flex items-center gap-3">
          <span className="grid h-11 w-11 place-items-center rounded-2xl bg-emerald-600 text-sm font-black text-white shadow-lg shadow-emerald-700/25">
            SM
          </span>
          <span className="min-w-0">
            <span className="block truncate text-base font-black text-slate-950">Stock Manager</span>
            <span className="block truncate text-xs font-semibold text-slate-500">Inventory operations</span>
          </span>
        </Link>
      </div>

      <nav className="min-h-0 flex-1 space-y-1 overflow-y-auto px-3 py-4">
        {navigation.map((item) => (
          <NavLink
            key={item.href}
            item={item}
            active={isActive(item.href)}
            onClick={onNavigate}
            t={t}
            isRtl={isRtl}
          />
        ))}
      </nav>

      <div className="border-t border-slate-100 p-4">
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-3">
          <p className="truncate text-sm font-bold text-slate-900">{user?.username || 'User'}</p>
          <Link
            href="/profile/"
            onClick={onNavigate}
            className="mt-1 inline-flex text-xs font-semibold text-emerald-700 hover:text-emerald-800"
          >
            {t('nav.profile', 'Manage Profile')}
          </Link>
        </div>

        <label className="mt-3 block text-xs font-bold uppercase text-slate-400">Language</label>
        <select
          value={language}
          onChange={(event) => setLanguage(event.target.value)}
          className="mt-1 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100"
        >
          {available.map((item) => (
            <option key={item.code} value={item.code}>
              {item.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}

export default function AppLayout({ title, subtitle, titleKey = null, subtitleKey = null, children }) {
  const { url, props } = usePage();
  const { t, language, direction, available, setLanguage } = useI18n();
  const [open, setOpen] = useState(false);
  const isRtl = direction === 'rtl';
  const user = props?.auth?.user || props?.user;
  const pageTitle = useMemo(() => (titleKey ? t(titleKey, title) : title), [t, titleKey, title]);
  const pageSubtitle = useMemo(() => (subtitleKey ? t(subtitleKey, subtitle) : subtitle), [t, subtitleKey, subtitle]);
  const isActive = (href) => (href === '/' ? url === '/' : url.startsWith(href.replace(/\/$/, '')));

  const sidebarProps = {
    t,
    language,
    available,
    setLanguage,
    user,
    isActive,
    isRtl,
    onNavigate: () => setOpen(false),
  };

  return (
    <div dir={direction} className="min-h-screen bg-slate-100 text-slate-900">
      <aside className={['fixed top-0 z-40 hidden h-full w-72 lg:block', isRtl ? 'right-0' : 'left-0'].join(' ')}>
        <Sidebar {...sidebarProps} />
      </aside>

      {open ? (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button
            type="button"
            aria-label="Close menu"
            className="absolute inset-0 bg-slate-950/40 backdrop-blur-sm"
            onClick={() => setOpen(false)}
          />
          <aside className={['absolute top-0 h-full w-80 max-w-[86vw]', isRtl ? 'right-0' : 'left-0'].join(' ')}>
            <Sidebar {...sidebarProps} />
          </aside>
        </div>
      ) : null}

      <main className={['min-h-screen transition-all', isRtl ? 'lg:pr-72' : 'lg:pl-72'].join(' ')}>
        <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-slate-100/85 backdrop-blur-xl">
          <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-4 sm:px-6 lg:px-8">
            <button
              type="button"
              aria-label="Open menu"
              onClick={() => setOpen(true)}
              className="grid h-11 w-11 place-items-center rounded-xl border border-slate-200 bg-white text-xl font-bold text-slate-700 shadow-sm transition hover:bg-slate-50 lg:hidden"
            >
              <Icon name="menu" className="h-5 w-5" />
            </button>

            <div className="min-w-0 flex-1">
              <p className="text-xs font-bold uppercase tracking-wide text-emerald-700">Workspace</p>
              <h1 className="truncate text-2xl font-black text-slate-950 sm:text-3xl">{pageTitle}</h1>
              {pageSubtitle ? <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-500">{pageSubtitle}</p> : null}
            </div>

            <div className="hidden items-center gap-3 rounded-2xl border border-slate-200 bg-white px-3 py-2 shadow-sm sm:flex">
              <span className="grid h-9 w-9 place-items-center rounded-xl bg-emerald-50 text-sm font-black text-emerald-700">
                {(user?.username || 'U').slice(0, 1).toUpperCase()}
              </span>
              <span className="min-w-0">
                <span className="block max-w-36 truncate text-sm font-bold text-slate-900">{user?.username || 'User'}</span>
                <span className="block text-xs font-medium text-slate-500">Active session</span>
              </span>
            </div>
          </div>
        </header>

        <section className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          {children}
        </section>
      </main>
    </div>
  );
}
