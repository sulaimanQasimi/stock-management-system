import React from 'react';
import {
  Alert,
  Badge as FlowbiteBadge,
  Button as FlowbiteButton,
  Card as FlowbiteCard,
  Label,
  Select,
  Table,
  Textarea,
  TextInput as FlowbiteTextInput,
} from 'flowbite-react';

export function cn(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(' ');
}

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'danger';
  loading?: boolean;
};

const buttonColors = {
  primary: 'success',
  secondary: 'light',
  danger: 'failure',
} as const;

export function Button({ className = '', variant = 'primary', loading = false, children, ...props }: ButtonProps) {
  return (
    <FlowbiteButton
      type="button"
      color={buttonColors[variant]}
      isProcessing={loading}
      disabled={loading || props.disabled}
      className={className}
      {...props}
    >
      {children}
    </FlowbiteButton>
  );
}

export function Card({ className = '', children }: { className?: string; children: React.ReactNode }) {
  return <FlowbiteCard className={className}>{children}</FlowbiteCard>;
}

export function Field({ label, htmlFor, error, children, hint }: { label: string; htmlFor: string; error?: string; hint?: string; children: React.ReactNode }) {
  return (
    <div className="mt-4">
      <Label htmlFor={htmlFor} color={error ? 'failure' : undefined} value={label} />
      <div className="mt-1">{children}</div>
      {hint ? <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{hint}</p> : null}
      {error ? <p className="mt-1 text-sm text-red-600 dark:text-red-500" role="alert">{error}</p> : null}
    </div>
  );
}

export function TextInput(props: React.ComponentProps<typeof FlowbiteTextInput>) {
  return <FlowbiteTextInput {...props} />;
}

export function SelectInput(props: React.ComponentProps<typeof Select>) {
  return <Select {...props} />;
}

export function TextAreaInput(props: React.ComponentProps<typeof Textarea>) {
  return <Textarea {...props} />;
}

export function ErrorSummary({ errors = {} }: { errors?: Record<string, unknown> }) {
  const messages = Object.values(errors).flatMap((value) => Array.isArray(value) ? value : value ? [String(value)] : []);
  if (!messages.length) return null;

  return (
    <Alert color="failure" className="mt-4" role="alert" aria-live="polite">
      {messages.map((message, index) => <p key={`${message}-${index}`}>{message}</p>)}
    </Alert>
  );
}

export function EmptyState({ title, description }: { title: string; description: string }) {
  return (
    <FlowbiteCard className="border-dashed text-center">
      <h3 className="text-base font-semibold text-gray-900 dark:text-white">{title}</h3>
      <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">{description}</p>
    </FlowbiteCard>
  );
}

const badgeColors = {
  success: 'success',
  danger: 'failure',
  info: 'info',
  neutral: 'gray',
} as const;

export function Badge({ children, tone = 'neutral' }: { children: React.ReactNode; tone?: 'success' | 'danger' | 'info' | 'neutral' }) {
  return <FlowbiteBadge color={badgeColors[tone]} className="inline-flex w-fit capitalize">{children}</FlowbiteBadge>;
}

export function TableShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800">
      <Table hoverable className="min-w-[760px] text-left">
        {children}
      </Table>
    </div>
  );
}
