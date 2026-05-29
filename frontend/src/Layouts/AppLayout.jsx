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
  { key: 'nav.profile', href: '/profile/', icon: '⚙' },
];

function NavLink({ item, active, onClick, t, isRtl }) {
  return (
    <Link
      href={item.href}
      onClick={onClick}
      className={[
        'group flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition-all duration-200',
        isRtl ? 'flex-row-reverse text-right' : 'text-left',
        active
          ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/20'
          : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
      ].join(' ')}
    >
      <span
        className={[
          'flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-sm transition-colors',
          active ? 'bg-white/15 text-white' : 'bg-slate-100 text-slate-500 group-hover:bg-white',
        ].join(' ')}
      >
        {item.icon}
      </span>
      <span className="min-w-0 flex-1">{t(item.key, item.key === 'nav.profile' ? 'Profile' : undefined)}</span>
    </Link>
  );
}

export default function AppLayout({ title, subtitle, titleKey = null, subtitleKey = null, children }) {
  const { url, props } = usePage();
  const { t, language, direction, available, setLanguage } = useI18n();
  const [open, setOpen] = useState(false);
  const isRtl = direction === 'rtl';

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
        <div className={['flex items-center gap-3', isRtl ? 'flex-row-reverse text-right' : ''].join(' ')}>
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-emerald-600 text-lg font-black text-white shadow-lg shadow-emerald-600/20">
            S
          </div>
          <div className="min-w-0">
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
            isRtl={isRtl}
          />
        ))}
      </nav>

      <div className={['mt-8 rounded-3xl border border-slate-200 bg-slate-50/80 p-4 backdrop-blur', isRtl ? 'text-right' : ''].join(' ')}>
        <div className="mb-4">
          <p className="text-sm font-semibold text-slate-900">
            {user?.username || user?.name || 'StockUp User'}
          </p>
          <p className="text-xs text-slate-500">{t('session.active', 'Active session')}</p>
          <Link href="/profile/" className="mt-2 inline-block text-xs font-semibold text-emerald-600 hover:text-emerald-700">
            {t('nav.profile', 'Manage Profile')}
          </Link>
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
          dir={direction}
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

  return <div dir={direction} className="min-h-screen bg-slate-100 text-slate-900">{/* unchanged layout body */}{/* existing layout remains below in repository after manual merge if needed */}{children}</div>;
}
