import React from 'react';
import { useForm } from '@inertiajs/react';
import AppLayout from '../Layouts/AppLayout';
import { Button, Card, EmptyState, Field, TableShell, TextAreaInput, TextInput } from '../Components/UI';

type Service = { id: number; name: string; price: string; description: string; is_active: boolean };

export default function Services({ services = [] }: { services: Service[] }) {
  const { data, setData, post, processing, reset, errors, recentlySuccessful } = useForm({ name: '', price: '', description: '', is_active: true as boolean });
  function submit(event: React.FormEvent) {
    event.preventDefault();
    post('/services/', { preserveScroll: true, onSuccess: () => reset() });
  }
  return (
    <AppLayout title="Services" subtitle="Create service names and prices that can be added to sales.">
      <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
        <Card>
          <form onSubmit={submit} noValidate>
            <h3 className="text-lg font-semibold text-slate-900">New service</h3>
            {recentlySuccessful ? <p className="mt-4 rounded-xl bg-emerald-50 p-3 text-sm text-emerald-700">Service saved successfully.</p> : null}
            <Field label="Service name" htmlFor="service-name" error={errors.name}><TextInput id="service-name" value={data.name} onChange={(e) => setData('name', e.target.value)} required /></Field>
            <Field label="Price" htmlFor="service-price" error={errors.price}><TextInput id="service-price" type="number" min="0" step="0.01" value={data.price} onChange={(e) => setData('price', e.target.value)} required /></Field>
            <Field label="Description" htmlFor="service-description" error={errors.description}><TextAreaInput id="service-description" rows={3} value={data.description} onChange={(e) => setData('description', e.target.value)} /></Field>
            <label className="mt-4 flex items-center gap-2 text-sm text-slate-700"><input type="checkbox" checked={data.is_active} onChange={(e) => setData('is_active', e.target.checked)} /> Active service</label>
            <Button type="submit" loading={processing} className="mt-5 w-full">Save service</Button>
          </form>
        </Card>
        {services.length ? <TableShell><thead className="bg-slate-50 text-slate-600"><tr><th className="px-4 py-3">Name</th><th className="px-4 py-3">Price</th><th className="px-4 py-3">Active</th><th className="px-4 py-3">Description</th></tr></thead><tbody className="divide-y divide-slate-100">{services.map((service) => <tr key={service.id} className="hover:bg-slate-50"><td className="px-4 py-3 font-medium text-slate-900">{service.name}</td><td className="px-4 py-3 text-slate-700">{service.price}</td><td className="px-4 py-3 text-slate-700">{service.is_active ? 'Yes' : 'No'}</td><td className="px-4 py-3 text-slate-600">{service.description || '—'}</td></tr>)}</tbody></TableShell> : <EmptyState title="No services yet" description="Create services like delivery, installation, repair, consultation, or setup fees." />}
      </div>
    </AppLayout>
  );
}
