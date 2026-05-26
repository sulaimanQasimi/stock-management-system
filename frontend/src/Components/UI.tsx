import React from 'react';

export function cn(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(' ');
}

export function Button({ className = '', variant = 'primary', loading = false, children, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' | 'danger'; loading?: boolean }) {
  const variants = {
    primary: 'bg-emerald-600 text-white hover:bg-emerald-700 focus:ring-emerald-500',
    secondary: 'bg-white text-slate-700 border border-slate-300 hover:bg-slate-50 focus:ring-slate-400',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
  };
  return (
    <button type="button" disabled={loading || props.disabled} className={cn('inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold shadow-sm transition focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60', variants[variant], className)} {...props}>
      {loading ? 'Please wait…' : children}
    </button>
  );
}

export function Card({ className = '', children }: { className?: string; children: React.ReactNode }) {
  return <div className={cn('rounded-2xl border border-slate-200 bg-white p-5 shadow-sm', className)}>{children}</div>;
}

export function Field({ label, htmlFor, error, children, hint }: { label: string; htmlFor: string; error?: string; hint?: string; children: React.ReactNode }) {
  return (
    <div className="mt-4">
      <label htmlFor={htmlFor} className="block text-sm font-medium text-slate-700">{label}</label>
      <div className="mt-1">{children}</div>
      {hint ? <p className="mt-1 text-xs text-slate-500">{hint}</p> : null}
      {error ? <p className="mt-1 text-sm text-red-600" role="alert">{error}</p> : null}
    </div>
  );
}

const inputClass = 'w-full rounded-xl border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20';

export function TextInput(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={cn(inputClass, props.className)} />;
}

export function SelectInput(props: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return <select {...props} className={cn(inputClass, props.className)} />;
}

export function TextAreaInput(props: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea {...props} className={cn(inputClass, props.className)} />;
}

export function ErrorSummary({ errors = {} }: { errors?: Record<string, unknown> }) {
  const messages = Object.values(errors).flatMap((value) => Array.isArray(value) ? value : value ? [String(value)] : []);
  if (!messages.length) return null;
  return (
    <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700" role="alert" aria-live="polite">
      {messages.map((message, index) => <p key={`${message}-${index}`}>{message}</p>)}
    </div>
  );
}

export function EmptyState({ title, description }: { title: string; description: string }) {
  return <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center"><h3 className="text-base font-semibold text-slate-900">{title}</h3><p className="mt-2 text-sm text-slate-500">{description}</p></div>;
}

export function Badge({ children, tone = 'neutral' }: { children: React.ReactNode; tone?: 'success' | 'danger' | 'info' | 'neutral' }) {
  const tones = {
    success: 'bg-emerald-50 text-emerald-700 ring-emerald-600/20',
    danger: 'bg-red-50 text-red-700 ring-red-600/20',
    info: 'bg-indigo-50 text-indigo-700 ring-indigo-600/20',
    neutral: 'bg-slate-100 text-slate-700 ring-slate-500/20',
  };
  return <span className={cn('inline-flex rounded-full px-2 py-1 text-xs font-semibold capitalize ring-1 ring-inset', tones[tone])}>{children}</span>;
}

export function TableShell({ children }: { children: React.ReactNode }) {
  return <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"><div className="overflow-x-auto"><table className="min-w-[760px] w-full text-left text-sm">{children}</table></div></div>;
}
