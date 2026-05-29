import React, { useState } from 'react';
import { Head, router } from '@inertiajs/react';

export default function Login({ databases = [], error = null }) {
  const [form, setForm] = useState({
    database: databases[0]?.value || 'default',
    username: '',
    password: '',
  });

  function submit(event) {
    event.preventDefault();

    router.post('/login/', form, {
      preserveScroll: true,
       headers: {
    'X-CSRFToken': document.cookie
      .split('; ')
      .find((row) => row.startsWith('csrftoken='))
      ?.split('=')[1] || '',
  },
    });
  }

  return (
    <>
      <Head title="Login" />

      <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4 py-10">
        <div className="w-full max-w-md overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-2xl shadow-slate-200/70">
          <div className="bg-gradient-to-br from-emerald-600 via-emerald-500 to-emerald-700 px-8 py-10 text-white">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-white/15 text-2xl font-black">
              S
            </div>

            <h1 className="mt-6 text-3xl font-black tracking-tight">
              StockUp
            </h1>

            <p className="mt-2 text-sm text-emerald-50">
              Login to your company database
            </p>
          </div>

          <form onSubmit={submit} className="space-y-5 px-8 py-8">
            {error ? (
              <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            ) : null}

            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700">
                Company Database
              </label>

              <select
                value={form.database}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    database: event.target.value,
                  }))
                }
                className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-emerald-500"
              >
                {databases.map((database) => (
                  <option key={database.value} value={database.value}>
                    {database.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700">
                Username
              </label>

              <input
                type="text"
                value={form.username}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    username: event.target.value,
                  }))
                }
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none transition focus:border-emerald-500"
                autoComplete="username"
                required
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700">
                Password
              </label>

              <input
                type="password"
                value={form.password}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    password: event.target.value,
                  }))
                }
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none transition focus:border-emerald-500"
                autoComplete="current-password"
                required
              />
            </div>

            <button
              type="submit"
              className="w-full rounded-2xl bg-emerald-600 px-4 py-3 text-sm font-bold text-white shadow-lg shadow-emerald-600/20 transition hover:bg-emerald-700"
            >
              Login
            </button>
          </form>
        </div>
      </div>
    </>
  );
}
