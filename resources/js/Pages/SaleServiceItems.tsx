import React from 'react';
import { useForm } from '@inertiajs/react';
import AppLayout from '../Layouts/AppLayout';
import { Button, Card, EmptyState, Field, SelectInput, TableShell, TextAreaInput, TextInput } from '../Components/UI';

type Option = { value: number; label: string; price?: string };
type Row = { id: number; sale: string; service: string; quantity: string; unit_price: string; total: string; note: string };

type Props = { saleServiceItems?: Row[]; options?: { sales?: Option[]; services?: Option[] } };

export default function SaleServiceItems({ saleServiceItems = [], options = {} }: Props) {
  const sales = options.sales || [];
  const services = options.services || [];
  const { data, setData, post, processing, reset, errors, recentlySuccessful } = useForm({ sale: '', service: '', quantity: '1', unit_price: '', note: '' });
  function changeService(value: string) {
    setData('service', value);
    const selected = services.find((service) => String(service.value) === value);
    if (selected?.price) setData('unit_price', selected.price);
  }
  function submit(event: React.FormEvent) {
    event.preventDefault();
    post('/sale-service-items/', { preserveScroll: true, onSuccess: () => reset() });
  }
  return (
    <AppLayout title="Sale Services" subtitle="Attach service charges to sales and include them in sale totals.">
      <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
        <Card>
          <form onSubmit={submit} noValidate>
            <h3 className="text-lg font-semibold text-slate-900">Add service to sale</h3>
            {recentlySuccessful ? <p className="mt-4 rounded-xl bg-emerald-50 p-3 text-sm text-emerald-700">Sale service saved successfully.</p> : null}
            <Field label="Sale" htmlFor="sale-service-sale" error={errors.sale}><SelectInput id="sale-service-sale" value={data.sale} onChange={(e) => setData('sale', e.target.value)} required><option value="">Select sale</option>{sales.map((sale) => <option key={sale.value} value={sale.value}>{sale.label}</option>)}</SelectInput></Field>
            <Field label="Service" htmlFor="sale-service-service" error={errors.service}><SelectInput id="sale-service-service" value={data.service} onChange={(e) => changeService(e.target.value)} required><option value="">Select service</option>{services.map((service) => <option key={service.value} value={service.value}>{service.label}</option>)}</SelectInput></Field>
            <Field label="Quantity" htmlFor="sale-service-quantity" error={errors.quantity}><TextInput id="sale-service-quantity" type="number" min="0.01" step="0.01" value={data.quantity} onChange={(e) => setData('quantity', e.target.value)} required /></Field>
            <Field label="Unit price" htmlFor="sale-service-price" error={errors.unit_price}><TextInput id="sale-service-price" type="number" min="0" step="0.01" value={data.unit_price} onChange={(e) => setData('unit_price', e.target.value)} required /></Field>
            <Field label="Note" htmlFor="sale-service-note" error={errors.note}><TextAreaInput id="sale-service-note" rows={3} value={data.note} onChange={(e) => setData('note', e.target.value)} /></Field>
            <Button type="submit" loading={processing} className="mt-5 w-full">Add service line</Button>
          </form>
        </Card>
        {saleServiceItems.length ? <TableShell><thead className="bg-slate-50 text-slate-600"><tr><th className="px-4 py-3">Sale</th><th className="px-4 py-3">Service</th><th className="px-4 py-3">Qty</th><th className="px-4 py-3">Price</th><th className="px-4 py-3">Total</th><th className="px-4 py-3">Note</th></tr></thead><tbody className="divide-y divide-slate-100">{saleServiceItems.map((item) => <tr key={item.id} className="hover:bg-slate-50"><td className="px-4 py-3 font-medium text-slate-900">{item.sale}</td><td className="px-4 py-3 text-slate-700">{item.service}</td><td className="px-4 py-3 text-slate-700">{item.quantity}</td><td className="px-4 py-3 text-slate-700">{item.unit_price}</td><td className="px-4 py-3 text-slate-900 font-semibold">{item.total}</td><td className="px-4 py-3 text-slate-600">{item.note || '—'}</td></tr>)}</tbody></TableShell> : <EmptyState title="No sale service lines yet" description="Add services like delivery, installation, repair, support, or setup fees to a sale." />}
      </div>
    </AppLayout>
  );
}
