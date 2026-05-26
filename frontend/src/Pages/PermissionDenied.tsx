import React from 'react';
import AppLayout from '../Layouts/AppLayout';

export default function PermissionDenied({ title = 'Permission denied' }: { title?: string }) {
  return (
    <AppLayout title={title} subtitle="You do not have permission to view or perform this action.">
      <div className="rounded-2xl border border-amber-200 bg-amber-50 p-6 text-amber-800">
        <h3 className="text-lg font-semibold">Access restricted</h3>
        <p className="mt-2 text-sm">Ask an administrator to grant the required StockUp permission for this page or action.</p>
      </div>
    </AppLayout>
  );
}
