import React from 'react';
import AppLayout from '../Layouts/AppLayout';
import { EmptyState } from '../Components/UI';

export default function Dashboard({ cards = [] }) {
  return (
    <AppLayout title="Dashboard" subtitle="Overview of stock, finance, sales, purchases, and profit reports.">
      {cards.length ? <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">{cards.map((card) => <div key={card.label} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"><p className="text-sm font-medium text-slate-500">{card.label}</p><p className="mt-2 text-3xl font-bold text-slate-900">{card.value}</p></div>)}</div> : <EmptyState title="No dashboard data" description="Dashboard metrics will appear after products, purchases, sales, and accounts are added." />}
      <div className="mt-6 grid gap-4 lg:grid-cols-3"><div className="rounded-2xl border border-emerald-100 bg-emerald-50 p-5"><h3 className="font-semibold text-emerald-900">Quick action</h3><p className="mt-1 text-sm text-emerald-700">Use Stock Movements to post audited increases, decreases, and transfers.</p></div><div className="rounded-2xl border border-slate-200 bg-white p-5"><h3 className="font-semibold text-slate-900">Operational focus</h3><p className="mt-1 text-sm text-slate-500">Review low stock, recent purchases, recent sales, and movement history daily.</p></div><div className="rounded-2xl border border-slate-200 bg-white p-5"><h3 className="font-semibold text-slate-900">Reports</h3><p className="mt-1 text-sm text-slate-500">Use reporting to audit profit, remaining stock value, and department transfers.</p></div></div>
    </AppLayout>
  );
}
