import React from 'react';

const baseInputClass = 'w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm outline-none transition focus:border-slate-900 focus:ring-2 focus:ring-slate-200';

export function Field({ label, error, children }) {
  return (
    <label className="block space-y-1">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      {children}
      {error ? <span className="text-xs text-red-600">{error}</span> : null}
    </label>
  );
}

export function TextInput({ label, error, ...props }) {
  return (
    <Field label={label} error={error}>
      <input className={baseInputClass} {...props} />
    </Field>
  );
}

export function NumberInput({ label, error, ...props }) {
  return (
    <Field label={label} error={error}>
      <input type="number" step="any" className={baseInputClass} {...props} />
    </Field>
  );
}

export function DateInput({ label, error, ...props }) {
  return (
    <Field label={label} error={error}>
      <input type="date" className={baseInputClass} {...props} />
    </Field>
  );
}

export function SelectInput({ label, options = [], error, placeholder = 'Select...', ...props }) {
  return (
    <Field label={label} error={error}>
      <select className={baseInputClass} {...props}>
        <option value="">{placeholder}</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>{option.label}</option>
        ))}
      </select>
    </Field>
  );
}

export function TextArea({ label, error, ...props }) {
  return (
    <Field label={label} error={error}>
      <textarea className={`${baseInputClass} min-h-28`} {...props} />
    </Field>
  );
}

export function PrimaryButton({ children, ...props }) {
  return (
    <button className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60" {...props}>
      {children}
    </button>
  );
}

export function SecondaryButton({ children, ...props }) {
  return (
    <button className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50" {...props}>
      {children}
    </button>
  );
}
