import React from 'react';
import { Link } from '@inertiajs/react';
import AppLayout from '../Layouts/AppLayout';
import { Button } from '../Components/UI';
import { useI18n } from '../i18n';

export default function PermissionDenied({ title = 'Permission denied' }: { title?: string }) {
  const { t } = useI18n();

  return (
    <AppLayout title={t('auth.permissionDenied', title)} subtitle={t('auth.permissionDeniedDescription')}>
      <div className="max-w-2xl rounded-2xl border border-amber-200 bg-amber-50 p-6 text-amber-900 shadow-sm" role="alert">
        <h3 className="text-lg font-semibold">{t('auth.accessRestricted')}</h3>
        <p className="mt-2 text-sm">{t('auth.askAdmin')}</p>
        <div className="mt-5 flex flex-wrap gap-3">
          <Link href="/" as="button" type="button" className="inline-flex items-center justify-center rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2">
            {t('auth.goDashboard')}
          </Link>
          <Button variant="secondary" onClick={() => window.history.back()}>{t('auth.goBack')}</Button>
        </div>
      </div>
    </AppLayout>
  );
}
