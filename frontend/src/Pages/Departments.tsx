import React from 'react';
import AppLayout from '../Layouts/AppLayout';

type Department = { id: number; name: string; code: string; description: string };

export default function Departments({ departments = [] }: { departments: Department[] }) {
  return (
    <AppLayout title="Departments" subtitle="Create and manage stock departments used by manual stock movements.">
      <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
        <form method="post" action="/departments/" className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="mb-4 text-lg font-semibold text-slate-900">New department</h3>
          <label className="block text-sm font-medium text-slate-700">Name</label>
          <input name="name" required className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" />
          <label className="mt-4 block text-sm font-medium text-slate-700">Code</label>
          <input name="code" className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" />
          <label className="mt-4 block text-sm font-medium text-slate-700">Description</label>
          <textarea name="description" className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" rows={4} />
          <button className="mt-5 rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white">Save department</button>
        </form>

        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr><th className="px-4 py-3">Name</th><th className="px-4 py-3">Code</th><th className="px-4 py-3">Description</th></tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {departments.map((department) => (
                <tr key={department.id}>
                  <td className="px-4 py-3 font-medium text-slate-900">{department.name}</td>
                  <td className="px-4 py-3 text-slate-600">{department.code}</td>
                  <td className="px-4 py-3 text-slate-600">{department.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </AppLayout>
  );
}
