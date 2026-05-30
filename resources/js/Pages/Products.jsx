import React from 'react';
import ModelCrudPage from './Shared/ModelCrudPage';

const fields = [
  { name: 'name', label: 'Name', type: 'text', required: true },
  { name: 'sku', label: 'SKU', type: 'text' },
  { name: 'barcode', label: 'Barcode', type: 'text' },
  { name: 'category', label: 'Category', type: 'select', optionsKey: 'categories' },
  { name: 'unit', label: 'Unit', type: 'select', optionsKey: 'units' },
  { name: 'quantity', label: 'Quantity', type: 'number' },
  { name: 'price', label: 'Cost Price', type: 'number' },
  { name: 'pack_sale_price', label: 'Pack Sale Price', type: 'number' },
  { name: 'unit_sale_price', label: 'Unit Sale Price', type: 'number' },
  { name: 'description', label: 'Description', type: 'textarea' },
];

const columns = [
  { key: 'name', label: 'Name' },
  { key: 'sku', label: 'SKU' },
  { key: 'barcode', label: 'Barcode' },
  { key: 'quantity', label: 'Quantity' },
  { key: 'price', label: 'Cost Price' },
  { key: 'pack_sale_price', label: 'Pack Sale' },
  { key: 'unit_sale_price', label: 'Unit Sale' },
];

export default function Products({ products = [], options = {} }) {
  return (
    <ModelCrudPage
      title="Products"
      subtitle="Manage products, stock quantities, barcodes, and pricing."
      records={products}
      fields={fields}
      columns={columns}
      options={options}
      routes={{ store: '/products/' }}
    />
  );
}
