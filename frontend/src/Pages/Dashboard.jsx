import React from 'react';
import AppLayout from '../Layouts/AppLayout';
import { Card, EmptyState } from '../Components/UI';

export default function Dashboard({ cards = [] }) {
  return (
    <AppLayout title="Dashboard" subtitle="Overview of stock, finance, sales, purchases, and profit reports.">
      {cards.length ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {cards.map((card) => (
            <Card key={card.label} className="transition hover:-translate-y-0.5 hover:shadow-md">
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{card.label}</p>
              <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">{card.value}</p>
            </Card>
          ))}
        </div>
      ) : <EmptyState title="No dashboard data" description="Dashboard metrics will appear after products, purchases, sales, and accounts are added." />}

      <div className="mt-6 grid gap-4 lg:grid-cols-3">
        <Card><h3 className="font-semibold text-gray-900 dark:text-white">Quick action</h3><p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Use Stock Movements to post audited increases and decreases.</p></Card>
        <Card><h3 className="font-semibold text-gray-900 dark:text-white">Operational focus</h3><p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Review low stock, recent purchases, recent sales, and movement history daily.</p></Card>
        <Card><h3 className="font-semibold text-gray-900 dark:text-white">Reports</h3><p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Use reporting to audit profit and remaining stock value.</p></Card>
      </div>
    </AppLayout>
  );
}
