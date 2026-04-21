import { useEffect, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

import { api, extractApiError } from '@/lib/api';
import { ConfirmButton } from '@/components/confirm-button';
import {
  Alert,
  Badge,
  Button,
  FormError,
  Input,
  Label,
  SectionHeader,
  Spinner,
  Surface,
} from '@/components/ui';

interface StaffUser {
  id: string;
  email: string;
  full_name: string;
  position: string | null;
  department: string | null;
  is_active: boolean;
}

const schema = z.object({
  email: z.string().trim().toLowerCase().email('Correo inválido'),
  full_name: z.string().trim().min(2, 'Nombre requerido'),
  position: z.string().trim().optional(),
  department: z.string().trim().optional(),
});
type FormValues = z.infer<typeof schema>;

export const StaffPage = () => {
  const qc = useQueryClient();
  const [alert, setAlert] = useState<{ kind: 'success' | 'error'; msg: string } | null>(
    null,
  );

  useEffect(() => {
    if (!alert) return;
    const t = window.setTimeout(() => setAlert(null), 4500);
    return () => window.clearTimeout(t);
  }, [alert]);

  const list = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const { data } = await api.get<{ items: StaffUser[] } | StaffUser[]>('/api/users/');
      return Array.isArray(data) ? data : data.items;
    },
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const create = useMutation({
    mutationFn: (values: FormValues) => api.post('/api/users/', values),
    onSuccess: () => {
      setAlert({ kind: 'success', msg: 'Staff creado correctamente.' });
      reset();
      qc.invalidateQueries({ queryKey: ['users'] });
    },
    onError: (err) => setAlert({ kind: 'error', msg: extractApiError(err) }),
  });

  const remove = useMutation({
    mutationFn: (id: string) => api.delete(`/api/users/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['users'] }),
    onError: (err) => setAlert({ kind: 'error', msg: extractApiError(err) }),
  });

  const items = list.data ?? [];

  return (
    <div className="space-y-14">
      <section aria-labelledby="alta-staff" className="space-y-5">
        <SectionHeader eyebrow="Personal" title="Alta de staff">
          Da de alta a un nuevo integrante del equipo. Recibirá acceso una vez
          asignado a un rol.
        </SectionHeader>

        <Surface className="p-5 md:p-6">
          <form
            id="alta-staff"
            onSubmit={handleSubmit((v) => create.mutate(v))}
            className="grid grid-cols-1 gap-x-6 gap-y-5 md:grid-cols-2"
            noValidate
          >
            <div>
              <Label htmlFor="email">Correo</Label>
              <Input
                id="email"
                type="email"
                autoComplete="email"
                aria-invalid={!!errors.email}
                {...register('email')}
              />
              <FormError message={errors.email?.message} />
            </div>
            <div>
              <Label htmlFor="full_name">Nombre completo</Label>
              <Input
                id="full_name"
                aria-invalid={!!errors.full_name}
                {...register('full_name')}
              />
              <FormError message={errors.full_name?.message} />
            </div>
            <div>
              <Label htmlFor="position">Puesto</Label>
              <Input
                id="position"
                placeholder="Recepcionista, chef, …"
                {...register('position')}
              />
            </div>
            <div>
              <Label htmlFor="department">Departamento</Label>
              <Input
                id="department"
                placeholder="Front office, A&B, …"
                {...register('department')}
              />
            </div>
            <div className="md:col-span-2 md:flex md:justify-end">
              <Button type="submit" disabled={isSubmitting || create.isPending}>
                {create.isPending ? <Spinner /> : 'Crear staff'}
              </Button>
            </div>
          </form>
        </Surface>

        {alert && <Alert kind={alert.kind}>{alert.msg}</Alert>}
      </section>

      <section aria-labelledby="staff-registrado" className="space-y-5">
        <SectionHeader
          eyebrow="Directorio"
          title="Staff registrado"
          meta={
            list.data && (
              <span>
                {items.length} {items.length === 1 ? 'persona' : 'personas'}
              </span>
            )
          }
        />

        {list.isLoading && <SkeletonRows rows={4} />}

        {list.isError && <Alert kind="error">{extractApiError(list.error)}</Alert>}

        {list.data && items.length === 0 && (
          <Surface className="p-8 text-center">
            <p className="font-display text-lg text-foreground">Aún sin personal</p>
            <p className="mx-auto mt-1 max-w-sm text-sm text-muted-foreground">
              Da de alta el primer integrante con el formulario de arriba; aparecerá
              aquí en cuanto se cree.
            </p>
          </Surface>
        )}

        {list.data && items.length > 0 && (
          <>
            {/* Mobile: stacked rows */}
            <ul className="space-y-3 md:hidden">
              {items.map((u) => (
                <Surface key={u.id} as="article" className="p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-medium text-foreground">{u.full_name}</p>
                      <p className="text-xs text-muted-foreground">{u.email}</p>
                    </div>
                    <ConfirmButton
                      label="Eliminar"
                      confirmLabel="Eliminar definitivamente"
                      onConfirm={() => remove.mutate(u.id)}
                      disabled={remove.isPending}
                    />
                  </div>
                  <dl className="mt-3 grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <dt className="text-muted-foreground">Puesto</dt>
                      <dd className="text-foreground">{u.position ?? '—'}</dd>
                    </div>
                    <div>
                      <dt className="text-muted-foreground">Departamento</dt>
                      <dd className="text-foreground">{u.department ?? '—'}</dd>
                    </div>
                  </dl>
                </Surface>
              ))}
            </ul>

            {/* Desktop: table */}
            <div className="hidden overflow-hidden rounded-lg border border-border md:block">
              <table className="w-full text-sm">
                <thead className="bg-muted/60 text-left text-2xs font-semibold uppercase tracking-wider text-muted-foreground">
                  <tr>
                    <th scope="col" className="px-4 py-3">
                      Nombre
                    </th>
                    <th scope="col" className="px-4 py-3">
                      Correo
                    </th>
                    <th scope="col" className="px-4 py-3">
                      Puesto
                    </th>
                    <th scope="col" className="px-4 py-3">
                      Departamento
                    </th>
                    <th scope="col" className="px-4 py-3">
                      Estado
                    </th>
                    <th scope="col" className="px-4 py-3 text-right">
                      <span className="sr-only">Acciones</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border bg-surface">
                  {items.map((u) => (
                    <tr key={u.id} className="transition-colors hover:bg-muted/40">
                      <td className="px-4 py-3 font-medium text-foreground">
                        {u.full_name}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">{u.email}</td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {u.position ?? '—'}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {u.department ?? '—'}
                      </td>
                      <td className="px-4 py-3">
                        <Badge tone={u.is_active ? 'success' : 'neutral'}>
                          {u.is_active ? 'Activo' : 'Baja'}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <ConfirmButton
                          label="Eliminar"
                          confirmLabel="Eliminar definitivamente"
                          onConfirm={() => remove.mutate(u.id)}
                          disabled={remove.isPending}
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </section>
    </div>
  );
};

const SkeletonRows = ({ rows = 3 }: { rows?: number }) => (
  <div className="overflow-hidden rounded-lg border border-border">
    <ul className="divide-y divide-border">
      {Array.from({ length: rows }).map((_, i) => (
        <li
          key={i}
          className="flex items-center justify-between gap-4 px-4 py-4"
          aria-hidden="true"
        >
          <div className="flex-1 space-y-2">
            <div className="h-3 w-1/3 animate-pulse rounded bg-muted" />
            <div className="h-2.5 w-1/4 animate-pulse rounded bg-muted/70" />
          </div>
          <div className="h-7 w-20 animate-pulse rounded bg-muted/70" />
        </li>
      ))}
    </ul>
  </div>
);
