import React, { FormEvent, useState } from 'react';
import { router } from '@inertiajs/react';
import AppLayout from '../Layouts/AppLayout';
import { Badge, Button, Card, EmptyState, TableShell, TextInput } from '../Components/UI';

type Product = {
  id: number;
  name: string;
  sku: string;
  barcode: string;
  category: string;
  unit: string;
  quantity: string;
  price: string;
  packSalePrice: string;
  unitSalePrice: string;
};

type Props = {
  query?: string;
  products?: Product[];
};

function stockTone(quantity: string) {
  return Number(quantity) > 0 ? 'success' : 'danger';
}

export default function ProductSearch({ query = '', products = [] }: Props) {
  const [term, setTerm] = useState(query);

  function submit(event: FormEvent) {
    event.preventDefault();
    router.get('/product-search/', { q: term }, { preserveState: true, replace: true });
  }

  function clearSearch() {
    setTerm('');
    router.get('/product-search/', {}, { preserveState: true, replace: true });
  }

  return (
    <AppLayout title="Product Search" subtitle="Find products quickly by barcode, SKU, name, category, or description.">
      <Card>
        <form onSubmit={submit} className="flex flex-col gap-3 lg:flex-row">
          <TextInput
            autoFocus
            value={term}
            onChange={(event) => setTerm(event.target.value)}
            placeholder="Scan barcode or type SKU, product name, or category..."
            aria-label="Search products"
          />
          <div className="flex gap-2">
            <Button type="submit">Search</Button>
            {query ? <Button type="button" variant="secondary" onClick={clearSearch}>Clear</Button> : null}
          </div>
        </form>
        <p className="mt-3 text-sm text-slate-500">
          Scanner tip: focus this box and scan a barcode. Most scanners submit text like keyboard input.
        </p>
      </Card>

      <div className="mt-6">
        {products.length ? (
          <TableShell>
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3">Product</th>
                <th className="px-4 py-3">SKU</th>
                <th className="px-4 py-3">Barcode</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3">Stock</th>
                <th className="px-4 py-3">Prices</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {products.map((product) => (
                <tr key={product.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3">
                    <p className="font-medium text-slate-900">{product.name}</p>
                    <p className="text-xs text-slate-500">{product.unit || 'No unit configured'}</p>
                  </td>
                  <td className="px-4 py-3 text-slate-700">{product.sku || '—'}</td>
                  <td className="px-4 py-3 font-mono text-xs text-slate-700">{product.barcode || '—'}</td>
                  <td className="px-4 py-3 text-slate-600">{product.category || '—'}</td>
                  <td className="px-4 py-3"><Badge tone={stockTone(product.quantity)}>{product.quantity}</Badge></td>
                  <td className="px-4 py-3 text-slate-700">
                    <div className="space-y-1 text-xs">
                      <p>Cost: {product.price}</p>
                      <p>Pack sale: {product.packSalePrice}</p>
                      <p>Unit sale: {product.unitSalePrice}</p>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </TableShell>
        ) : (
          <EmptyState
            title={query ? 'No matching products found' : 'Search for products'}
            description={query ? 'Try another barcode, SKU, product name, or category.' : 'Enter or scan a product identifier to begin.'}
          />
        )}
      </div>
    </AppLayout>
  );
}
