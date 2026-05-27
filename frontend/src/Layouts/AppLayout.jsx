import React, { useState } from 'react';
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
    <Link onClick={onClick} href={item.href} className={`flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-emerald-500/30 ${active ? 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-600/10' : 'text-slate-700 hover:bg-slate-100'}`}>
      <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-100 text-xs text-slate-600">{item.icon}</span>
      <span>{t(item.key)}</span>
    </Link>
  );
}

export default function AppLayout({ title, subtitle, titleKey, subtitleKey, children }) {
  const { url, props } = usePage();
  const { t, language, direction, available, setLanguage } = useI18n();
  const [open, setOpen] = useState(false);
  const user = props?.auth?.user || props?.user;
  const isActive = (href) => href === '/' ? url === '/' : url.startsWith(href.replace(/\/$/, ''));
  const pageTitle = titleKey ? t(titleKey, title) : title;
  const pageSubtitle = subtitleKey ? t(subtitleKey, subtitle) : subtitle;
  const sidebar = (
    <>
      <div className="mb-8">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-emerald-600 font-bold text-white shadow-sm">S</div>
          <div><h1 className="text-xl font-bold text-slate-900">{t('app.name', 'StockUp')}</h1><p className="text-xs text-slate-500">{t('app.tagline', 'Inventory command center')}</p></div>
        </div>
      </div>
      <nav className="space-y-2" aria-label="Primary navigation">{navigation.map((item) => <NavLink key={item.href} item={item} active={isActive(item.href)} onClick={() => setOpen(false)} t={t} />)}</nav>
      <div className="mt-8 rounded-2xl bg-slate-50 p-4 text-sm text-slate-600">
        <p className="font-semibold text-slate-900">{user?.username || user?.name || 'StockUp User'}</p>
        <label className="mt-3 block text-xs font-semibold text-slate-500" htmlFor="language-switcher">{t('language.label', 'Language')}</label>
        <select id="language-switcher" value={language} onChange={(event) => setLanguage(event.target.value)} className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-2 py-1 text-sm text-slate-700">
          {available.map((item) => <option key={item.code} value={item.code}>{item.label}</option>)}
        </select>
      </div>
    </>
  );
  return (
    <div dir={direction} className="min-h-screen bg-slate-100 text-slate-900">
      <aside className="fixed inset-y-0 left-0 hidden w-72 border-r border-slate-200 bg-white p-6 lg:block">{sidebar}</aside>
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 px-4 py-4 backdrop-blur lg:hidden"><div className="flex items-center justify-between"><Link href="/" className="flex items-center gap-2 font-bold text-slate-900"><span className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-600 text-white">S</span>{t('app.name', 'StockUp')}</Link><button type="button" onClick={() => setOpen(true)} className="rounded-xl border border-slate-300 px-3 py-2 text-sm font-semibold text-slate-700">Menu</button></div></header>
      {open ? <div className="fixed inset-0 z-40 bg-slate-900/40 lg:hidden" onClick={() => setOpen(false)} /> : null}
      <aside className={`fixed inset-y-0 left-0 z-50 w-80 max-w-[85vw] border-r border-slate-200 bg-white p-6 transition-transform lg:hidden ${open ? 'translate-x-0' : '-translate-x-full'}`}><div className="mb-4 flex justify-end"><button type="button" onClick={() => setOpen(false)} className="rounded-lg px-2 py-1 text-sm text-slate-500 hover:bg-slate-100">Close</button></div>{sidebar}</aside>
      <main className="lg:pl-72"><div className="border-b border-slate-200 bg-white px-4 py-5 sm:px-6"><div className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between"><div><h2 className="text-2xl font-bold tracking-tight text-slate-900">{pageTitle}</h2>{pageSubtitle ? <p className="mt-1 text-sm text-slate-500">{pageSubtitle}</p> : null}</div></div></div><section className="p-4 sm:p-6">{children}</section></main>
    </div>
  );
}
