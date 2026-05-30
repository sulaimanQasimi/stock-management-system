import React from 'react';
import { useForm } from '@inertiajs/react';
import AppLayout from '../Layouts/AppLayout';
import { Button, Card, EmptyState, ErrorSummary, Field, TableShell, TextAreaInput, TextInput } from '../Components/UI';

type Department = { id: number; name: string; code: string; description: string };

export default function Departments({ departments = [] }: { departments: Department[] }) {
  const { data, setData, post, processing, errors, reset, recentlySuccessful } = useForm({ name: '', code: '', description: '' });

  function submit(event: React.FormEvent) {
    event.preventDefault();
    post('/departments/', { preserveScroll: true, onSuccess: () => reset() });
  }

  return (
    <AppLayout title="Departments" subtitle="Create and manage departments used by manual stock movement and transfers.">
      <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
        <Card>
          <form onSubmit={submit} noValidate>
            <h3 className="text-lg font-semibold text-slate-900">New department</h3>
            <p className="mt-1 text-sm text-slate-500">Use departments to organize where stock is received, reduced, or transferred.</p>
            <ErrorSummary errors={errors} />
            {recentlySuccessful ? <p className="mt-4 rounded-xl bg-emerald-50 p-3 text-sm text-emerald-700" role="status">Department saved successfully.</p> : null}
            <Field label="Name" htmlFor="department-name" error={errors.name}><TextInput id="department-name" value={data.name} onChange={(event) => setData('name', event.target.value)} required autoComplete="off" /></Field>
            <Field label="Code" htmlFor="department-code" error={errors.code} hint="Optional short code, for example MAIN or WH-01."><TextInput id="department-code" value={data.code} onChange={(event) => setData('code', event.target.value)} autoComplete="off" /></Field>
            <Field label="Description" htmlFor="department-description" error={errors.description}><TextAreaInput id="department-description" value={data.description} onChange={(event) => setData('description', event.target.value)} rows={4} /></Field>
            <Button type="submit" loading={processing} className="mt-5 w-full">Save department</Button>
          </form>
        </Card>

        {departments.length ? (
          <TableShell>
            <thead className="bg-slate-50 text-slate-600"><tr><th className="px-4 py-3">Name</th><th className="px-4 py-3">Code</th><th className="px-4 py-3">Description</th></tr></thead>
            <tbody className="divide-y divide-slate-100">
              {departments.map((department) => <tr key={department.id} className="hover:bg-slate-50"><td className="px-4 py-3 font-medium text-slate-900">{department.name}</td><td className="px-4 py-3 text-slate-600">{department.code || '—'}</td><td className="px-4 py-3 text-slate-600">{department.description || '—'}</td></tr>)}
            </tbody>
          </TableShell>
        ) : <EmptyState title="No departments yet" description="Create your first department before posting transfers or department-based stock changes." />}
      </div>
    </AppLayout>
  );
}
