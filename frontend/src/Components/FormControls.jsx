import React from 'react';

const baseInputClass = 'w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm outline-none transition focus:border-slate-900 focus:ring-2 focus:ring-slate-200';

export function Field({ label, error, children }) {
  return (
    <label className="block space-y-1">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      {children}
      {error && <span className="text-xs text-red-600">{error}</span>}
    </label>
  );
}

function Control({ as: Component = 'input', label, error, className = '', ...props }) {
  return (
    <Field label={label} error={error}>
      <Component className={`${baseInputClass} ${className}`.trim()} {...props} />
    </Field>
  );
}

export const TextInput = (props) => <Control {...props} />;
export const NumberInput = (props) => <Control type="number" step="any" {...props} />;
export const DateInput = (props) => <Control type="date" {...props} />;
export const TextArea = (props) => <Control as="textarea" className="min-h-28" {...props} />;

export function SelectInput({ label, options = [], error, placeholder = 'Select...', ...props }) {
  return (
    <Control as="select" label={label} error={error} {...props}>
      <option value="">{placeholder}</option>
      {options.map(({ value, label }) => <option key={value} value={value}>{label}</option>)}
    </Control>
  );
}

const buttonClass = {
  primary: 'bg-slate-900 text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60',
  secondary: 'border border-slate-300 bg-white text-slate-700 hover:bg-slate-50',
};

function Button({ variant = 'primary', className = '', ...props }) {
  return <button className={`rounded-xl px-4 py-2 text-sm font-semibold shadow-sm transition ${buttonClass[variant]} ${className}`.trim()} {...props} />;
}

export const PrimaryButton = (props) => <Button {...props} />;
export const SecondaryButton = (props) => <Button variant="secondary" {...props} />;
