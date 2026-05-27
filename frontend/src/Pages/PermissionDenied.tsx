import React from 'react';
import { Link } from '@inertiajs/react';
import AppLayout from '../Layouts/AppLayout';
import { Button } from '../Components/UI';

export default function PermissionDenied({ title = 'Permission denied' }: { title?: string }) {
  return (
    <AppLayout title={title} subtitle="You do not have permission to view or perform this action.">
      <div className="max-w-2xl rounded-2xl border border-amber-200 bg-amber-50 p-6 text-amber-900 shadow-sm" role="alert">
        <h3 className="text-lg font-semibold">Access restricted</h3>
        <p className="mt-2 text-sm">Ask an administrator to grant the required StockUp permission for this page or action.</p>
        <div className="mt-5 flex flex-wrap gap-3">
          <Link href="/" as="button" type="button" className="inline-flex items-center justify-center rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2">
            Go to dashboard
          </Link>
          <Button variant="secondary" onClick={() => window.history.back()}>Go back</Button>
        </div>
      </div>
    </AppLayout>
  );
}
