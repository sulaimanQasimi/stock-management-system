import React, { useMemo, useState } from 'react';
import AppLayout from '../Layouts/AppLayout';

type Option = { value: number; label: string };
type Movement = {
  id: number;
  product: string;
  movement_type: 'increase' | 'decrease' | 'transfer';
  quantity: string;
  from_department: string;
  to_department: string;
  reference_number: string;
  reason: string;
  movement_date: string;
};

type Props = {
  stockMovements?: Movement[];
  options?: { products?: Option[]; departments?: Option[] };
  errors?: Record<string, string[] | string>;
};

function csrfToken() {
  return document.cookie
    .split('; ')
    .find((row) => row.startsWith('csrftoken='))
    ?.split('=')[1];
}

export default function StockMovements({ stockMovements = [], options = {}, errors = {} }: Props) {
  const [movementType, setMovementType] = useState<'increase' | 'decrease' | 'transfer'>('increase');
  const products = options.products ?? [];
  const departments = options.departments ?? [];
  const errorMessages = useMemo(() => Object.values(errors).flat().filter(Boolean), [errors]);

  return (
    <AppLayout title="Stock Movements" subtitle="Manually increase stock, decrease stock, or transfer stock between departments with an audit trail.">
      <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
        <form method="post" action="/stock-movements/" className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken() ?? ''} />
          <h3 className="text-lg font-semibold text-slate-900">Post stock movement</h3>
          <p className="mt-1 text-sm text-slate-500">Movements are locked after posting. Add a correction movement if a mistake is made.</p>

          {errorMessages.length ? (
            <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              {errorMessages.map((message, index) => <p key={index}>{message}</p>)}
            </div>
          ) : null}

          <label className="mt-4 block text-sm font-medium text-slate-700">Movement type</label>
          <select name="movement_type" value={movementType} onChange={(event) => setMovementType(event.target.value as typeof movementType)} className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2">
            <option value="increase">Increase stock</option>
            <option value="decrease">Decrease stock</option>
            <option value="transfer">Transfer department</option>
          </select>

          <label className="mt-4 block text-sm font-medium text-slate-700">Product</label>
          <select name="product" required className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2">
            <option value="">Select product</option>
            {products.map((product) => <option key={product.value} value={product.value}>{product.label}</option>)}
          </select>

          <label className="mt-4 block text-sm font-medium text-slate-700">Quantity</label>
          <input name="quantity" required type="number" min="0.01" step="0.01" className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" />

          {movementType !== 'increase' ? (
            <>
              <label className="mt-4 block text-sm font-medium text-slate-700">From department</label>
              <select name="from_department" required className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2">
                <option value="">Select source department</option>
                {departments.map((department) => <option key={department.value} value={department.value}>{department.label}</option>)}
              </select>
            </>
          ) : null}

          {movementType !== 'decrease' ? (
            <>
              <label className="mt-4 block text-sm font-medium text-slate-700">To department</label>
              <select name="to_department" required className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2">
                <option value="">Select receiving department</option>
                {departments.map((department) => <option key={department.value} value={department.value}>{department.label}</option>)}
              </select>
            </>
          ) : null}

          <label className="mt-4 block text-sm font-medium text-slate-700">Reference number</label>
          <input name="reference_number" className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" />

          <label className="mt-4 block text-sm font-medium text-slate-700">Reason</label>
          <input name="reason" placeholder="Adjustment, damage, opening stock, department transfer..." className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" />

          <label className="mt-4 block text-sm font-medium text-slate-700">Note</label>
          <textarea name="note" rows={3} className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" />

          <button className="mt-5 w-full rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white">Post movement</button>
        </form>

        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3">Date</th><th className="px-4 py-3">Product</th><th className="px-4 py-3">Type</th><th className="px-4 py-3">Qty</th><th className="px-4 py-3">From</th><th className="px-4 py-3">To</th><th className="px-4 py-3">Reason</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {stockMovements.map((movement) => (
                <tr key={movement.id}>
                  <td className="px-4 py-3 text-slate-600">{movement.movement_date}</td>
                  <td className="px-4 py-3 font-medium text-slate-900">{movement.product}</td>
                  <td className="px-4 py-3 capitalize text-slate-700">{movement.movement_type}</td>
                  <td className="px-4 py-3 text-slate-700">{movement.quantity}</td>
                  <td className="px-4 py-3 text-slate-600">{movement.from_department || '—'}</td>
                  <td className="px-4 py-3 text-slate-600">{movement.to_department || '—'}</td>
                  <td className="px-4 py-3 text-slate-600">{movement.reason || movement.reference_number}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </AppLayout>
  );
}
