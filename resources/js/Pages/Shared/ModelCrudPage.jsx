import React from 'react';
import { useForm } from '@inertiajs/react';
import AppLayout from '../../Layouts/AppLayout';
import { DateInput, NumberInput, PrimaryButton, SelectInput, TextArea, TextInput } from '../../Components/FormControls';
import { useI18n } from '../../i18n';

const fieldComponents = {
  select: SelectInput,
  date: DateInput,
  number: NumberInput,
  textarea: TextArea,
  text: TextInput,
};

const getDefaultValue = (field) => (field.type === 'number' ? 0 : '');

const normalizeOptions = (items = []) => items.map((item) => {
  if (item && typeof item === 'object') {
    return {
      value: item.value ?? item.id ?? '',
      label: item.label ?? item.name ?? item.code ?? item.title ?? String(item.value ?? item.id ?? ''),
    };
  }

  return { value: item, label: String(item) };
}).filter((item) => item.value !== '');

const pluralize = (value) => {
  if (!value) return '';
  if (value.endsWith('y')) return `${value.slice(0, -1)}ies`;
  if (value.endsWith('s')) return value;
  return `${value}s`;
};

const defaultPropKey = (title) => {
  const words = title.replace(/([a-z])([A-Z])/g, '$1 $2').split(/\s+/).filter(Boolean);
  if (!words.length) return 'records';

  const [first, ...rest] = words;
  return `${first.charAt(0).toLowerCase()}${first.slice(1)}${rest.join('')}`;
};
const titleKeys = {
  Categories: 'categories.title',
  Units: 'units.title',
  Parties: 'parties.title',
  Products: 'products.title',
  PurchaseBatches: 'purchases.title',
  PurchaseItems: 'purchases.title',
  PurchasePayments: 'finance.purchasePayments',
  Sales: 'sales.title',
  SaleItems: 'sales.title',
  SalePayments: 'finance.salePayments',
  StockProfitReports: 'reports.title',
  Currencies: 'finance.currencies',
  Accounts: 'finance.accounts',
  Transactions: 'finance.transactions',
  ExpenseTypes: 'finance.expenseTypes',
  Expenses: 'finance.expenses',
};

function optionListFor(field, options, props) {
  if (field.type !== 'select') return [];
  const key = field.optionsKey || field.name;
  const candidates = [
    options[key],
    props[key],
    props[pluralize(key)],
    field.options,
  ];

  return normalizeOptions(candidates.find((items) => Array.isArray(items)) || []);
}

function renderField(field, data, setData, errors, options, props) {
  const Component = fieldComponents[field.type] || TextInput;
  const extraProps = field.type === 'select'
    ? {
      options: optionListFor(field, options, props),
      placeholder: `Select ${field.label}`,
    }
    : {};

  return (
    <Component
      label={field.label}
      name={field.name}
      value={data[field.name] ?? getDefaultValue(field)}
      error={errors[field.name]}
      onChange={(event) => setData(field.name, event.target.value)}
      required={field.required}
      {...extraProps}
    />
  );
}

export default function ModelCrudPage(props) {
  const { title, subtitle, fields = [], columns = [], options = {}, routes = {}, initial = {}, propKey } = props;
  const { t } = useI18n();
  const recordKey = propKey || defaultPropKey(title);
  const records = props.records || props[recordKey] || [];
  const defaultData = fields.reduce((values, field) => {
    values[field.name] = initial[field.name] ?? getDefaultValue(field);
    return values;
  }, {});

  const { data, setData, post, processing, errors, reset } = useForm(defaultData);
  const localizedTitle = titleKeys[title] ? t(titleKeys[title], title) : title;

  const submit = (event) => {
    event.preventDefault();
    if (!routes.store) return;
    post(routes.store, {
      forceFormData: true,
      preserveScroll: true,
      onSuccess: () => reset(),
    });
  };

  return (
    <AppLayout title={localizedTitle} subtitle={subtitle}>
      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_420px]">
        <div className="rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 px-5 py-4">
            <h3 className="text-lg font-semibold text-slate-900">{t('records.title')}</h3>
            <p className="text-sm text-slate-500">{t('records.description')}</p>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50">
                <tr>
                  {columns.map((column) => (
                    <th key={column.key} className="px-4 py-3 text-left font-semibold text-slate-600">{column.label}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {records.length === 0 ? (
                  <tr>
                    <td colSpan={columns.length || 1} className="px-4 py-8 text-center text-slate-500">{t('records.none')}</td>
                  </tr>
                ) : records.map((record) => (
                  <tr key={record.id} className="hover:bg-slate-50">
                    {columns.map((column) => (
                      <td key={column.key} className="whitespace-nowrap px-4 py-3 text-slate-700">{record[column.key] ?? t('common.none')}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <form onSubmit={submit} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-5">
            <h3 className="text-lg font-semibold text-slate-900">{t('common.create')} {localizedTitle}</h3>
            <p className="text-sm text-slate-500">{t('form.generated')}</p>
          </div>
          <div className="space-y-4">
            {fields.map((field) => (
              <div key={field.name}>{renderField(field, data, setData, errors, options, props)}</div>
            ))}
          </div>
          <div className="mt-6 flex justify-end">
            <PrimaryButton type="submit" disabled={processing || !routes.store}>{t('form.save')}</PrimaryButton>
          </div>
        </form>
      </div>
    </AppLayout>
  );
}
