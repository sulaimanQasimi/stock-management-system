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
  return <Link href={item.href} onClick={onClick} className={[ 'group flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition-all duration-200', isRtl ? 'flex-row-reverse text-right' : 'text-left', active ? 'bg-emerald-600 text-white' : 'text-slate-600 hover:bg-slate-100' ].join(' ')}><span>{item.icon}</span><span className="min-w-0 flex-1">{t(item.key, item.key === 'nav.profile' ? 'Profile' : undefined)}</span></Link>;
}

export default function AppLayout({ title, subtitle, titleKey = null, subtitleKey = null, children }) {
  const { url, props } = usePage();
  const { t, language, direction, available, setLanguage } = useI18n();
  const [open, setOpen] = useState(false);
  const isRtl = direction === 'rtl';
  const user = props?.auth?.user || props?.user;
  const pageTitle = useMemo(() => (titleKey ? t(titleKey, title) : title), [t, titleKey, title]);
  const pageSubtitle = useMemo(() => (subtitleKey ? t(subtitleKey, subtitle) : subtitle), [t, subtitleKey, subtitle]);
  const isActive = (href) => href === '/' ? url === '/' : url.startsWith(href.replace(/\/$/, ''));

  const sidebar = <><nav className="space-y-2">{navigation.map((item)=><NavLink key={item.href} item={item} active={isActive(item.href)} onClick={()=>setOpen(false)} t={t} isRtl={isRtl} />)}</nav><div className="mt-8"><p>{user?.username}</p><Link href="/profile/">{t('nav.profile','Manage Profile')}</Link><select value={language} onChange={(e)=>setLanguage(e.target.value)}>{available.map((item)=><option key={item.code} value={item.code}>{item.label}</option>)}</select></div></>;

  return <div dir={direction} className="min-h-screen bg-slate-100 text-slate-900"><aside className={isRtl ? 'fixed right-0 top-0 h-full w-72 bg-white hidden lg:block' : 'fixed left-0 top-0 h-full w-72 bg-white hidden lg:block'}>{sidebar}</aside><main className={isRtl ? 'lg:pr-72' : 'lg:pl-72'}><div className="p-4"><h2 className="text-3xl font-black">{pageTitle}</h2>{pageSubtitle ? <p>{pageSubtitle}</p> : null}</div><section className="p-4">{children}</section></main></div>;
}
