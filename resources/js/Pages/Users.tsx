import React, { useMemo, useState } from 'react';
import { router } from '@inertiajs/react';
import AppLayout from '../Layouts/AppLayout';
import { Badge, EmptyState, TableShell } from '../Components/UI';

type Permission = {
  id: number;
  codename: string;
  name: string;
};

type PermissionGroup = {
  group: string;
  permissions: Permission[];
};

type User = {
  id: number;
  username: string;
  email: string;
  firstName?: string;
  lastName?: string;
  isActive: boolean;
  isStaff: boolean;
  isSuperuser: boolean;
  permissionIds: number[];
};

export default function Users({ users = [], permissions = [], auth }) {
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  const emptyForm = {
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    is_active: true,
    is_staff: false,
    is_superuser: false,
    permissions: [] as number[],
  };

  const [createForm, setCreateForm] = useState(emptyForm);

  function togglePermission(currentPermissions: number[], permissionId: number) {
    return currentPermissions.includes(permissionId)
      ? currentPermissions.filter((id) => id !== permissionId)
      : [...currentPermissions, permissionId];
  }

  function submitCreate(event) {
    event.preventDefault();

    router.post('/users/', {
      ...createForm,
      permissions: createForm.permissions,
    });
  }

  function submitUpdate(event) {
    event.preventDefault();

    router.post(`/users/${selectedUser.id}/update/`, {
      ...selectedUser,
      permissions: selectedUser.permissionIds,
    });
  }

  const stats = useMemo(() => ({
    total: users.length,
    admins: users.filter((user) => user.isSuperuser).length,
    staff: users.filter((user) => user.isStaff).length,
    active: users.filter((user) => user.isActive).length,
  }), [users]);

  return (
    <AppLayout
      title="User Management"
      subtitle={`Manage users and permissions inside ${auth?.database || 'current'} database.`}
    >
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard title="Total Users" value={stats.total} />
        <StatCard title="Administrators" value={stats.admins} />
        <StatCard title="Staff Users" value={stats.staff} />
        <StatCard title="Active Accounts" value={stats.active} />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.1fr,0.9fr]">
        <div className="space-y-6">
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-slate-900">Tenant Users</h3>
                <p className="text-sm text-slate-500">
                  Users are isolated inside the selected company database.
                </p>
              </div>

              <Badge tone="success">{auth?.database}</Badge>
            </div>

            {users.length ? (
              <TableShell>
                <thead className="bg-slate-50 text-slate-600">
                  <tr>
                    <th className="px-4 py-3">User</th>
                    <th className="px-4 py-3">Role</th>
                    <th className="px-4 py-3">Status</th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-slate-100">
                  {users.map((user) => (
                    <tr
                      key={user.id}
                      className="cursor-pointer hover:bg-slate-50"
                      onClick={() => setSelectedUser(user)}
                    >
                      <td className="px-4 py-3">
                        <div>
                          <p className="font-semibold text-slate-900">
                            {user.username}
                          </p>
                          <p className="text-xs text-slate-500">
                            {user.email || 'No email'}
                          </p>
                        </div>
                      </td>

                      <td className="px-4 py-3">
                        {user.isSuperuser ? (
                          <Badge tone="danger">Super Admin</Badge>
                        ) : user.isStaff ? (
                          <Badge tone="info">Staff</Badge>
                        ) : (
                          <Badge tone="neutral">Standard</Badge>
                        )}
                      </td>

                      <td className="px-4 py-3">
                        {user.isActive ? (
                          <Badge tone="success">Active</Badge>
                        ) : (
                          <Badge tone="danger">Disabled</Badge>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </TableShell>
            ) : (
              <EmptyState
                title="No users found"
                description="Create your first tenant-local user account."
              />
            )}
          </div>
        </div>

        <div className="space-y-6">
          <UserForm
            title="Create User"
            description="Create a new user inside the current tenant database."
            form={createForm}
            setForm={setCreateForm}
            permissions={permissions}
            onSubmit={submitCreate}
          />

          {selectedUser ? (
            <UserForm
              title={`Edit ${selectedUser.username}`}
              description="Update user details and fine-grained permissions."
              form={selectedUser}
              setForm={setSelectedUser}
              permissions={permissions}
              onSubmit={submitUpdate}
              submitLabel="Save Changes"
            />
          ) : null}
        </div>
      </div>
    </AppLayout>
  );
}

function StatCard({ title, value }) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <p className="text-sm font-medium text-slate-500">{title}</p>
      <p className="mt-2 text-4xl font-black tracking-tight text-slate-900">
        {value}
      </p>
    </div>
  );
}

function UserForm({
  title,
  description,
  form,
  setForm,
  permissions,
  onSubmit,
  submitLabel = 'Create User',
}) {
  return (
    <form
      onSubmit={onSubmit}
      className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
    >
      <div className="mb-5">
        <h3 className="text-lg font-bold text-slate-900">{title}</h3>
        <p className="text-sm text-slate-500">{description}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Field label="Username">
          <input
            value={form.username || ''}
            onChange={(event) =>
              setForm((current) => ({
                ...current,
                username: event.target.value,
              }))
            }
            className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm"
          />
        </Field>

        <Field label="Email">
          <input
            value={form.email || ''}
            onChange={(event) =>
              setForm((current) => ({
                ...current,
                email: event.target.value,
              }))
            }
            className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm"
          />
        </Field>

        <Field label="First Name">
          <input
            value={form.first_name || form.firstName || ''}
            onChange={(event) =>
              setForm((current) => ({
                ...current,
                first_name: event.target.value,
                firstName: event.target.value,
              }))
            }
            className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm"
          />
        </Field>

        <Field label="Last Name">
          <input
            value={form.last_name || form.lastName || ''}
            onChange={(event) =>
              setForm((current) => ({
                ...current,
                last_name: event.target.value,
                lastName: event.target.value,
              }))
            }
            className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm"
          />
        </Field>
      </div>

      <Field label="Password">
        <input
          type="password"
          value={form.password || ''}
          onChange={(event) =>
            setForm((current) => ({
              ...current,
              password: event.target.value,
            }))
          }
          className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm"
        />
      </Field>

      <div className="mt-5 grid gap-3 md:grid-cols-3">
        <Toggle
          label="Active"
          checked={form.is_active ?? form.isActive}
          onChange={(checked) =>
            setForm((current) => ({
              ...current,
              is_active: checked,
              isActive: checked,
            }))
          }
        />

        <Toggle
          label="Staff"
          checked={form.is_staff ?? form.isStaff}
          onChange={(checked) =>
            setForm((current) => ({
              ...current,
              is_staff: checked,
              isStaff: checked,
            }))
          }
        />

        <Toggle
          label="Superuser"
          checked={form.is_superuser ?? form.isSuperuser}
          onChange={(checked) =>
            setForm((current) => ({
              ...current,
              is_superuser: checked,
              isSuperuser: checked,
            }))
          }
        />
      </div>

      <div className="mt-6">
        <h4 className="text-sm font-bold uppercase tracking-wide text-slate-500">
          Fine-Grained Permissions
        </h4>

        <div className="mt-4 max-h-[420px] space-y-5 overflow-y-auto pr-2">
          {permissions.map((group) => (
            <div
              key={group.group}
              className="rounded-2xl border border-slate-200 p-4"
            >
              <h5 className="text-sm font-bold text-slate-900">
                {group.group}
              </h5>

              <div className="mt-3 grid gap-2">
                {group.permissions.map((permission) => {
                  const selected = (form.permissions || form.permissionIds || []).includes(permission.id);

                  return (
                    <label
                      key={permission.id}
                      className="flex items-start gap-3 rounded-xl px-3 py-2 transition hover:bg-slate-50"
                    >
                      <input
                        type="checkbox"
                        checked={selected}
                        onChange={() => {
                          const next = selected
                            ? (form.permissions || form.permissionIds || []).filter((id) => id !== permission.id)
                            : [...(form.permissions || form.permissionIds || []), permission.id];

                          setForm((current) => ({
                            ...current,
                            permissions: next,
                            permissionIds: next,
                          }))
                        }}
                        className="mt-1"
                      />

                      <div>
                        <p className="text-sm font-medium text-slate-900">
                          {permission.name}
                        </p>
                        <p className="text-xs text-slate-500">
                          {permission.codename}
                        </p>
                      </div>
                    </label>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      <button
        type="submit"
        className="mt-6 w-full rounded-2xl bg-emerald-600 px-4 py-3 text-sm font-bold text-white"
      >
        {submitLabel}
      </button>
    </form>
  );
}

function Field({ label, children }) {
  return (
    <div>
      <label className="mb-2 block text-sm font-semibold text-slate-700">
        {label}
      </label>
      {children}
    </div>
  );
}

function Toggle({ label, checked, onChange }) {
  return (
    <label className="flex items-center gap-3 rounded-2xl border border-slate-200 px-4 py-3 text-sm font-medium text-slate-700">
      <input
        type="checkbox"
        checked={checked}
        onChange={(event) => onChange(event.target.checked)}
      />
      {label}
    </label>
  );
}
