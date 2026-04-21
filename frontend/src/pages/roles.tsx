import { useEffect, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { api, extractApiError } from '@/lib/api';
import { ChipInput } from '@/components/chip-input';
import {
  Alert,
  Badge,
  Button,
  Input,
  Label,
  SectionHeader,
  Spinner,
  Surface,
  Textarea,
} from '@/components/ui';

interface Role {
  id: string;
  name: string;
  description: string | null;
  permissions: string[];
}

const PERMISSION_SUGGESTIONS = [
  'users:read',
  'users:write',
  'users:delete',
  'roles:read',
  'roles:write',
  'audit:read',
  'agent:ask',
];

export const RolesPage = () => {
  const qc = useQueryClient();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [permissions, setPermissions] = useState<string[]>([]);
  const [alert, setAlert] = useState<{ kind: 'success' | 'error'; msg: string } | null>(
    null,
  );

  useEffect(() => {
    if (!alert) return;
    const t = window.setTimeout(() => setAlert(null), 4500);
    return () => window.clearTimeout(t);
  }, [alert]);

  const roles = useQuery({
    queryKey: ['roles'],
    queryFn: async () => (await api.get<Role[]>('/api/roles')).data,
  });

  const create = useMutation({
    mutationFn: () =>
      api.post('/api/roles', {
        name: name.trim(),
        description: description.trim() || null,
        permissions,
      }),
    onSuccess: () => {
      setAlert({ kind: 'success', msg: 'Rol creado.' });
      setName('');
      setDescription('');
      setPermissions([]);
      qc.invalidateQueries({ queryKey: ['roles'] });
    },
    onError: (err) => setAlert({ kind: 'error', msg: extractApiError(err) }),
  });

  const items = roles.data ?? [];

  return (
    <div className="space-y-14">
      <section aria-labelledby="nuevo-rol" className="space-y-5">
        <SectionHeader eyebrow="RBAC" title="Nuevo rol">
          Define un rol y sus permisos. Los permisos siguen el formato{' '}
          <code className="font-mono text-foreground">recurso:acción</code>.
        </SectionHeader>

        <Surface className="p-5 md:p-6">
          <form
            id="nuevo-rol"
            onSubmit={(e) => {
              e.preventDefault();
              if (name.trim()) create.mutate();
            }}
            className="grid grid-cols-1 gap-x-6 gap-y-5 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]"
          >
            <div className="space-y-5">
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
                <Textarea
                  id="role-desc"
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Acceso completo a operación, sin alta de roles."
                />
              </div>
            </div>

            <div className="space-y-3">
              <Label htmlFor="role-perms">Permisos</Label>
              <ChipInput
                id="role-perms"
                value={permissions}
                onChange={setPermissions}
                suggestions={PERMISSION_SUGGESTIONS}
                placeholder="Escribe y presiona Enter"
                describedBy="role-perms-help"
              />
              <p id="role-perms-help" className="text-xs text-muted-foreground">
                Enter o coma para agregar; Backspace para borrar el último.
              </p>
            </div>

            <div className="lg:col-span-2 lg:flex lg:justify-end">
              <Button type="submit" disabled={create.isPending || !name.trim()}>
                {create.isPending ? <Spinner /> : 'Crear rol'}
              </Button>
            </div>
          </form>
        </Surface>

        {alert && <Alert kind={alert.kind}>{alert.msg}</Alert>}
      </section>

      <section aria-labelledby="roles-existentes" className="space-y-5">
        <SectionHeader
          eyebrow="Catálogo"
          title="Roles existentes"
          meta={
            roles.data && (
              <span>
                {items.length} {items.length === 1 ? 'rol' : 'roles'}
              </span>
            )
          }
        />

        {roles.isLoading && (
          <div className="grid gap-4 md:grid-cols-2">
            {Array.from({ length: 2 }).map((_, i) => (
              <Surface key={i} className="space-y-3 p-5">
                <div className="h-4 w-1/3 animate-pulse rounded bg-muted" />
                <div className="h-3 w-2/3 animate-pulse rounded bg-muted/70" />
                <div className="flex gap-2">
                  <div className="h-5 w-16 animate-pulse rounded bg-muted/60" />
                  <div className="h-5 w-20 animate-pulse rounded bg-muted/60" />
                </div>
              </Surface>
            ))}
          </div>
        )}
        {roles.isError && <Alert kind="error">{extractApiError(roles.error)}</Alert>}
        {roles.data && items.length === 0 && (
          <Surface className="p-8 text-center">
            <p className="font-display text-lg text-foreground">Sin roles definidos</p>
            <p className="mx-auto mt-1 max-w-sm text-sm text-muted-foreground">
              Crea el primer rol para empezar a controlar el acceso al panel.
            </p>
          </Surface>
        )}
        {roles.data && items.length > 0 && (
          <ul className="grid gap-4 md:grid-cols-2">
            {items.map((r) => (
              <li key={r.id}>
                <Surface as="article" className="h-full p-5">
                  <h3 className="font-display text-lg font-medium text-foreground">
                    {r.name}
                  </h3>
                  {r.description ? (
                    <p className="mt-1 max-w-prose text-sm text-muted-foreground">
                      {r.description}
                    </p>
                  ) : (
                    <p className="mt-1 text-xs italic text-muted-foreground">
                      Sin descripción
                    </p>
                  )}
                  <div className="mt-4 flex flex-wrap gap-1.5">
                    {r.permissions.length === 0 ? (
                      <Badge>sin permisos</Badge>
                    ) : (
                      r.permissions.map((p) => (
                        <Badge key={p} tone="accent" className="font-mono">
                          {p}
                        </Badge>
                      ))
                    )}
                  </div>
                </Surface>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
};
