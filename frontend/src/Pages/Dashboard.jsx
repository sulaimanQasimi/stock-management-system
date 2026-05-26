import React from 'react';
import AppLayout from '../Layouts/AppLayout';

export default function Dashboard({ cards = [] }) {
  return (
    <AppLayout title="Dashboard" subtitle="Overview of stock, finance, sales, purchases, and profit reports.">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {cards.map((card) => (
          <div key={card.label} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm font-medium text-slate-500">{card.label}</p>
            <p className="mt-2 text-3xl font-bold text-slate-900">{card.value}</p>
          </div>
        ))}
      </div>
    </AppLayout>
  );
}
