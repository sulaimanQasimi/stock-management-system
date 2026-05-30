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

export function Button({
  className = '',
  variant = 'primary',
  loading = false,
  children,
  ...props
}: ButtonProps) {
  return (
    <FlowbiteButton
      type="button"
      color={buttonColors[variant]}
      isProcessing={loading}
      disabled={loading || props.disabled}
      className={cn('font-semibold transition-transform hover:scale-[0.99]', className)}
      {...props}
    >
      {children}
    </FlowbiteButton>
  );
}

type CardProps = React.PropsWithChildren<{
  className?: string;
}>;

export function Card({
  className = '',
  children,
}: CardProps) {
  return (
    <FlowbiteCard
      className={cn(
        'rounded-3xl border border-slate-200 bg-white shadow-sm transition-all duration-200 hover:shadow-md',
        className,
      )}
    >
      {children}
    </FlowbiteCard>
  );
}

export function Field({
  label,
  htmlFor,
  error,
  children,
  hint,
}: {
  label: string;
  htmlFor: string;
  error?: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="mt-4">
      <Label
        htmlFor={htmlFor}
        color={error ? 'failure' : undefined}
        value={label}
        className="text-sm font-semibold text-slate-700"
      />

      <div className="mt-2">{children}</div>

      {hint ? (
        <p className="mt-1 text-xs text-slate-500">{hint}</p>
      ) : null}

      {error ? (
        <p className="mt-1 text-sm text-red-600" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}

export function TextInput(props: React.ComponentProps<typeof FlowbiteTextInput>) {
  return <FlowbiteTextInput sizing="md" {...props} />;
}

export function SelectInput(props: React.ComponentProps<typeof Select>) {
  return <Select sizing="md" {...props} />;
}

export function TextAreaInput(props: React.ComponentProps<typeof Textarea>) {
  return <Textarea rows={4} {...props} />;
}

export function ErrorSummary({
  errors = {},
}: {
  errors?: Record<string, unknown>;
}) {
  const messages = Object.values(errors).flatMap((value) =>
    Array.isArray(value) ? value : value ? [String(value)] : [],
  );

  if (!messages.length) return null;

  return (
    <Alert
      color="failure"
      className="mt-4 rounded-2xl border border-red-100"
      role="alert"
      aria-live="polite"
    >
      <div className="space-y-1">
        {messages.map((message, index) => (
          <p key={`${message}-${index}`}>{message}</p>
        ))}
      </div>
    </Alert>
  );
}

export function EmptyState({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-3xl border border-dashed border-slate-300 bg-slate-50 px-6 py-10 text-center">
      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-white shadow-sm">
        📦
      </div>

      <h3 className="mt-4 text-base font-bold text-slate-900">{title}</h3>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
        {description}
      </p>
    </div>
  );
}

const badgeColors = {
  success: 'success',
  danger: 'failure',
  info: 'info',
  neutral: 'gray',
} as const;

export function Badge({
  children,
  tone = 'neutral',
}: {
  children: React.ReactNode;
  tone?: 'success' | 'danger' | 'info' | 'neutral';
}) {
  return (
    <FlowbiteBadge
      color={badgeColors[tone]}
      className="inline-flex w-fit rounded-full px-2.5 py-1 capitalize"
    >
      {children}
    </FlowbiteBadge>
  );
}

export function TableShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
      <div className="overflow-x-auto">
        <Table hoverable className="min-w-[760px] text-left text-sm">
          {children}
        </Table>
      </div>
    </div>
  );
}
