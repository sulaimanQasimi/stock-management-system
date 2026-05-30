import React, { FormEvent, useState } from 'react';
import { router } from '@inertiajs/react';
import AppLayout from '../Layouts/AppLayout';
import { Badge, Button, Card, EmptyState, TableShell, TextInput } from '../Components/UI';
import { useI18n } from '../i18n';

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
  const { t } = useI18n();

  function submit(event: FormEvent) {
    event.preventDefault();
    router.get('/product-search/', { q: term }, { preserveState: true, replace: true });
  }

  function clearSearch() {
    setTerm('');
    router.get('/product-search/', {}, { preserveState: true, replace: true });
  }

  return (
    <AppLayout titleKey="productSearch.title" subtitleKey="productSearch.subtitle" title="Product Search" subtitle="Find products quickly by barcode, SKU, name, category, or description.">
      <Card>
        <form onSubmit={submit} className="flex flex-col gap-3 lg:flex-row">
          <TextInput
            autoFocus
            value={term}
            onChange={(event) => setTerm(event.target.value)}
            placeholder={t('productSearch.placeholder')}
            aria-label={t('productSearch.search')}
          />
          <div className="flex gap-2">
            <Button type="submit">{t('productSearch.search')}</Button>
            {query ? <Button type="button" variant="secondary" onClick={clearSearch}>{t('productSearch.clear')}</Button> : null}
          </div>
        </form>
        <p className="mt-3 text-sm text-slate-500">{t('productSearch.scannerTip')}</p>
      </Card>

      <div className="mt-6">
        {products.length ? (
          <TableShell>
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3">{t('table.product')}</th>
                <th className="px-4 py-3">{t('table.sku')}</th>
                <th className="px-4 py-3">{t('table.barcode')}</th>
                <th className="px-4 py-3">{t('table.category')}</th>
                <th className="px-4 py-3">{t('table.stock')}</th>
                <th className="px-4 py-3">{t('table.prices')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {products.map((product) => (
                <tr key={product.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3">
                    <p className="font-medium text-slate-900">{product.name}</p>
                    <p className="text-xs text-slate-500">{product.unit || t('table.noUnit')}</p>
                  </td>
                  <td className="px-4 py-3 text-slate-700">{product.sku || t('common.none')}</td>
                  <td className="px-4 py-3 font-mono text-xs text-slate-700">{product.barcode || t('common.none')}</td>
                  <td className="px-4 py-3 text-slate-600">{product.category || t('common.none')}</td>
                  <td className="px-4 py-3"><Badge tone={stockTone(product.quantity)}>{product.quantity}</Badge></td>
                  <td className="px-4 py-3 text-slate-700">
                    <div className="space-y-1 text-xs">
                      <p>{t('table.cost')}: {product.price}</p>
                      <p>{t('table.packSale')}: {product.packSalePrice}</p>
                      <p>{t('table.unitSale')}: {product.unitSalePrice}</p>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </TableShell>
        ) : (
          <EmptyState
            title={query ? t('productSearch.noMatchTitle') : t('productSearch.emptyTitle')}
            description={query ? t('productSearch.noMatchDescription') : t('productSearch.emptyDescription')}
          />
        )}
      </div>
    </AppLayout>
  );
}
