import React, { useState } from 'react';
import { router } from '@inertiajs/react';
import AppLayout from '../Layouts/AppLayout';

export default function Profile({ profile, status, errors = {} }) {
  const [details, setDetails] = useState({
    username: profile?.username || '',
    email: profile?.email || '',
    first_name: profile?.firstName || '',
    last_name: profile?.lastName || '',
  });

  const [passwords, setPasswords] = useState({
    current_password: '',
    password: '',
    password_confirmation: '',
  });

  return (
    <AppLayout
      title="Profile Management"
      subtitle="Manage your account information, security settings, and personal details."
    >
      <div className="grid gap-6 xl:grid-cols-[1fr,1fr]">
        <form
          onSubmit={(event) => {
            event.preventDefault();
            router.post('/profile/', {
              action: 'profile',
              ...details,
            });
          }}
          className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <h3 className="text-xl font-bold text-slate-900">Account Details</h3>

          {status ? (
            <div className="mt-4 rounded-2xl bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
              {status}
            </div>
          ) : null}

          <div className="mt-6 grid gap-4">
            <Field label="Username" error={errors.username?.[0]}>
              <input
                value={details.username}
                onChange={(e) => setDetails((v) => ({ ...v, username: e.target.value }))}
                className="w-full rounded-2xl border border-slate-200 px-4 py-3"
              />
            </Field>

            <Field label="Email" error={errors.email?.[0]}>
              <input
                value={details.email}
                onChange={(e) => setDetails((v) => ({ ...v, email: e.target.value }))}
                className="w-full rounded-2xl border border-slate-200 px-4 py-3"
              />
            </Field>

            <Field label="First Name">
              <input
                value={details.first_name}
                onChange={(e) => setDetails((v) => ({ ...v, first_name: e.target.value }))}
                className="w-full rounded-2xl border border-slate-200 px-4 py-3"
              />
            </Field>

            <Field label="Last Name">
              <input
                value={details.last_name}
                onChange={(e) => setDetails((v) => ({ ...v, last_name: e.target.value }))}
                className="w-full rounded-2xl border border-slate-200 px-4 py-3"
              />
            </Field>
          </div>

          <button className="mt-6 rounded-2xl bg-emerald-600 px-5 py-3 font-bold text-white">
            Save Profile
          </button>
        </form>

        <form
          onSubmit={(event) => {
            event.preventDefault();
            router.post('/profile/', {
              action: 'password',
              ...passwords,
            });
          }}
          className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <h3 className="text-xl font-bold text-slate-900">Security</h3>

          <div className="mt-6 grid gap-4">
            <Field label="Current Password" error={errors.current_password?.[0]}>
              <input
                type="password"
                value={passwords.current_password}
                onChange={(e) => setPasswords((v) => ({ ...v, current_password: e.target.value }))}
                className="w-full rounded-2xl border border-slate-200 px-4 py-3"
              />
            </Field>

            <Field label="New Password" error={errors.password?.[0]}>
              <input
                type="password"
                value={passwords.password}
                onChange={(e) => setPasswords((v) => ({ ...v, password: e.target.value }))}
                className="w-full rounded-2xl border border-slate-200 px-4 py-3"
              />
            </Field>

            <Field label="Confirm Password" error={errors.password_confirmation?.[0]}>
              <input
                type="password"
                value={passwords.password_confirmation}
                onChange={(e) => setPasswords((v) => ({ ...v, password_confirmation: e.target.value }))}
                className="w-full rounded-2xl border border-slate-200 px-4 py-3"
              />
            </Field>
          </div>

          <button className="mt-6 rounded-2xl bg-slate-900 px-5 py-3 font-bold text-white">
            Change Password
          </button>
        </form>
      </div>
    </AppLayout>
  );
}

function Field({ label, error, children }) {
  return (
    <div>
      <label className="mb-2 block text-sm font-semibold text-slate-700">{label}</label>
      {children}
      {error ? <p className="mt-2 text-sm text-red-600">{error}</p> : null}
    </div>
  );
}
