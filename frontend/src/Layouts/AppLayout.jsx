import React from 'react';
import { Link } from '@inertiajs/react';

const navigation = [
  { label: 'Dashboard', href: '/' },
  { label: 'Products', href: '/products/' },
  { label: 'Stock Movements', href: '/stock-movements/' },
  { label: 'Departments', href: '/departments/' },
  { label: 'Purchases', href: '/purchase-batches/' },
  { label: 'Sales', href: '/sales/' },
  { label: 'Finance', href: '/accounts/' },
  { label: 'Reports', href: '/stock-profit-reports/' },
];

export default function AppLayout({ title, subtitle, children }) {
  return (
    <div className="min-h-screen bg-slate-100">
      <aside className="fixed inset-y-0 left-0 hidden w-72 border-r border-slate-200 bg-white p-6 lg:block">
        <div className="mb-8">
          <h1 className="text-xl font-bold text-slate-900">Stock Manager</h1>
          <p className="text-sm text-slate-500">Inventory, finance, sales, reports</p>
        </div>
        <nav className="space-y-2">
          {navigation.map((item) => (
            <Link key={item.href} href={item.href} className="block rounded-xl px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100">
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>

      <main className="lg:pl-72">
        <header className="border-b border-slate-200 bg-white px-6 py-5">
          <h2 className="text-2xl font-bold text-slate-900">{title}</h2>
          {subtitle ? <p className="mt-1 text-sm text-slate-500">{subtitle}</p> : null}
        </header>
        <section className="p-6">{children}</section>
      </main>
    </div>
  );
}
