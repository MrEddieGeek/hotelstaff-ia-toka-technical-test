import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { api, extractApiError } from '@/lib/api';
import { Alert, Button, Card, Input, Label, Spinner } from '@/components/ui';

interface Role {
  id: string;
  name: string;
  description: string | null;
  permissions: string[];
}

export const RolesPage = () => {
  const qc = useQueryClient();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [permissions, setPermissions] = useState('');
  const [alert, setAlert] = useState<{ kind: 'success' | 'error'; msg: string } | null>(null);

  const roles = useQuery({
    queryKey: ['roles'],
    queryFn: async () => (await api.get<Role[]>('/api/roles')).data,
  });

  const create = useMutation({
    mutationFn: () =>
      api.post('/api/roles', {
        name,
        description: description || null,
        permissions: permissions
          .split(',')
          .map((p) => p.trim())
          .filter(Boolean),
      }),
    onSuccess: () => {
      setAlert({ kind: 'success', msg: 'Rol creado.' });
      setName('');
      setDescription('');
      setPermissions('');
      qc.invalidateQueries({ queryKey: ['roles'] });
    },
    onError: (err) => setAlert({ kind: 'error', msg: extractApiError(err) }),
  });

  return (
    <div className="space-y-8">
      <section>
        <h2 className="mb-4 text-xl font-semibold text-slate-900">Nuevo rol</h2>
        <Card>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (name.trim()) create.mutate();
            }}
            className="space-y-4"
          >
            <div>
              <Label htmlFor="role-name">Nombre</Label>
              <Input
                id="role-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="gerente-general"
                required
              />
            </div>
            <div>
              <Label htmlFor="role-desc">Descripción</Label>
              <Input
                id="role-desc"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="role-perms">Permisos (separados por coma)</Label>
              <Input
                id="role-perms"
                value={permissions}
                onChange={(e) => setPermissions(e.target.value)}
                placeholder="users:read, users:write, audit:read"
              />
            </div>
            <Button type="submit" disabled={create.isPending || !name.trim()}>
              {create.isPending ? <Spinner /> : 'Crear rol'}
            </Button>
          </form>
        </Card>
        {alert && (
          <div className="mt-4">
            <Alert kind={alert.kind}>{alert.msg}</Alert>
          </div>
        )}
      </section>

      <section>
        <h2 className="mb-4 text-xl font-semibold text-slate-900">Roles existentes</h2>
        {roles.isLoading && <p className="text-slate-500">Cargando…</p>}
        {roles.isError && <Alert kind="error">{extractApiError(roles.error)}</Alert>}
        {roles.data && roles.data.length === 0 && <Alert kind="info">No hay roles aún.</Alert>}
        {roles.data && (
          <div className="grid gap-4 md:grid-cols-2">
            {roles.data.map((r) => (
              <Card key={r.id}>
                <h3 className="text-lg font-semibold text-slate-900">{r.name}</h3>
                {r.description && <p className="mt-1 text-sm text-slate-600">{r.description}</p>}
                <div className="mt-3 flex flex-wrap gap-2">
                  {r.permissions.map((p) => (
                    <span
                      key={p}
                      className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-700"
                    >
                      {p}
                    </span>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};
