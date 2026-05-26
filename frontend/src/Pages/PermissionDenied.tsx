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
        <div className="mt-5 flex flex-wrap gap-3"><Link href="/"><Button variant="secondary">Go to dashboard</Button></Link><Button variant="secondary" onClick={() => window.history.back()}>Go back</Button></div>
      </div>
    </AppLayout>
  );
}
