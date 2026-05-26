import React from 'react';
import { Link } from '@inertiajs/react';
import AppLayout from '../Layouts/AppLayout';
import { EmptyState, TableShell } from '../Components/UI';

type User = { id: number; username: string; email: string };

export default function Users({ users = [] }: { users: User[] }) {
  return (
    <AppLayout title="Users" subtitle="Review active application users and account contact details.">
      {users.length ? <TableShell><thead className="bg-slate-50 text-slate-600"><tr><th className="px-4 py-3">User</th><th className="px-4 py-3">Email</th></tr></thead><tbody className="divide-y divide-slate-100">{users.map((user) => <tr key={user.id} className="hover:bg-slate-50"><td className="px-4 py-3 font-medium text-slate-900"><Link className="text-emerald-700 hover:text-emerald-800" href={`/users/${user.id}`}>{user.username}</Link></td><td className="px-4 py-3 text-slate-600">{user.email || '—'}</td></tr>)}</tbody></TableShell> : <EmptyState title="No users found" description="Active users will appear here after they are created." />}
    </AppLayout>
  );
}
