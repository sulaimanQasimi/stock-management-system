import React, { useMemo } from 'react';
import { useForm } from '@inertiajs/react';
import AppLayout from '../Layouts/AppLayout';
import { Badge, Button, Card, EmptyState, ErrorSummary, Field, SelectInput, TableShell, TextAreaInput, TextInput } from '../Components/UI';

type Option = { value: number; label: string; quantity?: string };
type Movement = { id: number; product: string; movement_type: 'increase' | 'decrease' | 'transfer'; quantity: string; from_department: string; to_department: string; reference_number: string; reason: string; movement_date: string };
type Props = { stockMovements?: Movement[]; options?: { products?: Option[]; departments?: Option[] }; errors?: Record<string, string[] | string> };

const tone = { increase: 'success', decrease: 'danger', transfer: 'info' } as const;

export default function StockMovements({ stockMovements = [], options = {}, errors: pageErrors = {} }: Props) {
  const products = options.products ?? [];
  const departments = options.departments ?? [];
  const { data, setData, post, processing, errors, reset, recentlySuccessful } = useForm({ movement_type: 'increase', product: '', quantity: '', from_department: '', to_department: '', reference_number: '', reason: '', note: '' });
  const mergedErrors = { ...pageErrors, ...errors };
  const selectedProduct = useMemo(() => products.find((product) => String(product.value) === data.product), [products, data.product]);
  const helper = data.movement_type === 'increase' ? 'Adds stock to the selected receiving department and product ledger.' : data.movement_type === 'decrease' ? 'Removes stock from the selected source department and product ledger.' : 'Moves stock between departments without changing total product stock.';

  function submit(event: React.FormEvent) {
    event.preventDefault();
    const action = data.movement_type === 'decrease' ? 'Decrease stock now?' : data.movement_type === 'transfer' ? 'Transfer stock now?' : null;
    if (action && !window.confirm(action)) return;
    post('/stock-movements/', { preserveScroll: true, onSuccess: () => reset() });
  }

  return (
    <AppLayout title="Stock Movements" subtitle="Post audited stock increases, decreases, and department transfers.">
      <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
        <Card>
          <form onSubmit={submit} noValidate>
            <h3 className="text-lg font-semibold text-slate-900">Post movement</h3>
            <p className="mt-1 text-sm text-slate-500">Movements are immutable. Add a correction movement if a mistake is made.</p>
            <ErrorSummary errors={mergedErrors} />
            {recentlySuccessful ? <p className="mt-4 rounded-xl bg-emerald-50 p-3 text-sm text-emerald-700" role="status">Stock movement posted successfully.</p> : null}

            <Field label="Movement type" htmlFor="movement-type" hint={helper} error={errors.movement_type}>
              <SelectInput id="movement-type" value={data.movement_type} onChange={(event) => setData('movement_type', event.target.value)}>
                <option value="increase">Increase stock</option><option value="decrease">Decrease stock</option><option value="transfer">Transfer department</option>
              </SelectInput>
            </Field>

            <Field label="Product" htmlFor="movement-product" error={errors.product}>
              <SelectInput id="movement-product" value={data.product} onChange={(event) => setData('product', event.target.value)} required>
                <option value="">Select product</option>{products.map((product) => <option key={product.value} value={product.value}>{product.label}{product.quantity ? ` — ${product.quantity} in stock` : ''}</option>)}
              </SelectInput>
            </Field>
            {selectedProduct?.quantity ? <p className="mt-2 rounded-xl bg-slate-50 p-3 text-sm text-slate-600">Current stock: <strong>{selectedProduct.quantity}</strong></p> : null}

            <Field label="Quantity" htmlFor="movement-quantity" error={errors.quantity}><TextInput id="movement-quantity" value={data.quantity} onChange={(event) => setData('quantity', event.target.value)} required type="number" min="0.01" step="0.01" inputMode="decimal" /></Field>

            {data.movement_type !== 'increase' ? <Field label="From department" htmlFor="from-department" error={errors.from_department}><SelectInput id="from-department" value={data.from_department} onChange={(event) => setData('from_department', event.target.value)} required><option value="">Select source department</option>{departments.map((department) => <option key={department.value} value={department.value}>{department.label}</option>)}</SelectInput></Field> : null}
            {data.movement_type !== 'decrease' ? <Field label="To department" htmlFor="to-department" error={errors.to_department}><SelectInput id="to-department" value={data.to_department} onChange={(event) => setData('to_department', event.target.value)} required><option value="">Select receiving department</option>{departments.map((department) => <option key={department.value} value={department.value}>{department.label}</option>)}</SelectInput></Field> : null}

            <Field label="Reference number" htmlFor="reference-number" error={errors.reference_number}><TextInput id="reference-number" value={data.reference_number} onChange={(event) => setData('reference_number', event.target.value)} /></Field>
            <Field label="Reason" htmlFor="movement-reason" error={errors.reason}><TextInput id="movement-reason" value={data.reason} onChange={(event) => setData('reason', event.target.value)} placeholder="Adjustment, damage, opening stock, department transfer..." /></Field>
            <Field label="Note" htmlFor="movement-note" error={errors.note}><TextAreaInput id="movement-note" value={data.note} onChange={(event) => setData('note', event.target.value)} rows={3} /></Field>
            <Button type="submit" loading={processing} className="mt-5 w-full">Post movement</Button>
          </form>
        </Card>

        {stockMovements.length ? <TableShell><thead className="bg-slate-50 text-slate-600"><tr><th className="px-4 py-3">Date</th><th className="px-4 py-3">Product</th><th className="px-4 py-3">Type</th><th className="px-4 py-3">Qty</th><th className="px-4 py-3">From</th><th className="px-4 py-3">To</th><th className="px-4 py-3">Reason</th></tr></thead><tbody className="divide-y divide-slate-100">{stockMovements.map((movement) => <tr key={movement.id} className="hover:bg-slate-50"><td className="px-4 py-3 text-slate-600">{movement.movement_date}</td><td className="px-4 py-3 font-medium text-slate-900">{movement.product}</td><td className="px-4 py-3"><Badge tone={tone[movement.movement_type]}>{movement.movement_type}</Badge></td><td className="px-4 py-3 text-slate-700">{movement.quantity}</td><td className="px-4 py-3 text-slate-600">{movement.from_department || '—'}</td><td className="px-4 py-3 text-slate-600">{movement.to_department || '—'}</td><td className="px-4 py-3 text-slate-600">{movement.reason || movement.reference_number || '—'}</td></tr>)}</tbody></TableShell> : <EmptyState title="No stock movements yet" description="Post the first movement to start the audited stock ledger." />}
      </div>
    </AppLayout>
  );
}
