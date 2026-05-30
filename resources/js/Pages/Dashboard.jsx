import React from 'react';
import AppLayout from '../Layouts/AppLayout';
import { Card, EmptyState } from '../Components/UI';
import { useI18n } from '../i18n';

export default function Dashboard({ cards = [] }) {
  const { t } = useI18n();

  return (
    <AppLayout titleKey="dashboard.title" subtitleKey="dashboard.subtitle" title="Dashboard" subtitle="Overview of stock, finance, sales, purchases, and profit reports.">
      {cards.length ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {cards.map((card) => (
            <Card key={card.label} className="transition hover:-translate-y-0.5 hover:shadow-md">
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{card.translationKey ? t(card.translationKey, card.label) : card.label}</p>
              <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">{card.value}</p>
            </Card>
          ))}
        </div>
      ) : <EmptyState title={t('dashboard.noDataTitle')} description={t('dashboard.noDataDescription')} />}

      <div className="mt-6 grid gap-4 lg:grid-cols-3">
        <Card><h3 className="font-semibold text-gray-900 dark:text-white">{t('dashboard.quickAction')}</h3><p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{t('dashboard.quickActionDescription')}</p></Card>
        <Card><h3 className="font-semibold text-gray-900 dark:text-white">{t('dashboard.operationalFocus')}</h3><p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{t('dashboard.operationalFocusDescription')}</p></Card>
        <Card><h3 className="font-semibold text-gray-900 dark:text-white">{t('dashboard.reports')}</h3><p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{t('dashboard.reportsDescription')}</p></Card>
      </div>
    </AppLayout>
  );
}
