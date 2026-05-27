import React from 'react';
import { Button as FlowbiteButton, Label, Select, Textarea, TextInput as FlowbiteTextInput } from 'flowbite-react';

export function Field({ label, error, children }) {
  return (
    <div className="space-y-1">
      <Label color={error ? 'failure' : undefined} value={label} />
      {children}
      {error ? <span className="text-xs text-red-600 dark:text-red-500">{error}</span> : null}
    </div>
  );
}

function Control({ component: Component = FlowbiteTextInput, label, error, ...props }) {
  return (
    <Field label={label} error={error}>
      <Component color={error ? 'failure' : undefined} {...props} />
    </Field>
  );
}

export const TextInput = (props) => <Control {...props} />;
export const NumberInput = (props) => <Control type="number" step="any" {...props} />;
export const DateInput = (props) => <Control type="date" {...props} />;
export const TextArea = (props) => <Control component={Textarea} rows={4} {...props} />;

export function SelectInput({ label, options = [], error, placeholder = 'Select...', ...props }) {
  return (
    <Control component={Select} label={label} error={error} {...props}>
      <option value="">{placeholder}</option>
      {options.map(({ value, label }) => <option key={value} value={value}>{label}</option>)}
    </Control>
  );
}

function Button({ variant = 'primary', ...props }) {
  return <FlowbiteButton color={variant === 'secondary' ? 'light' : 'dark'} {...props} />;
}

export const PrimaryButton = (props) => <Button {...props} />;
export const SecondaryButton = (props) => <Button variant="secondary" {...props} />;
