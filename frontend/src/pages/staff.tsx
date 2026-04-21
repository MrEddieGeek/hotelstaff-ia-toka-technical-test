import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

import { api, extractApiError } from '@/lib/api';
import { Alert, Button, Card, FormError, Input, Label, Spinner } from '@/components/ui';

interface StaffUser {
  id: string;
  email: string;
  full_name: string;
  position: string | null;
  department: string | null;
  is_active: boolean;
}

const schema = z.object({
  email: z.string().email('Correo inválido'),
  full_name: z.string().min(2, 'Nombre requerido'),
  position: z.string().optional(),
  department: z.string().optional(),
});
type FormValues = z.infer<typeof schema>;

export const StaffPage = () => {
  const qc = useQueryClient();
  const [alert, setAlert] = useState<{ kind: 'success' | 'error'; msg: string } | null>(null);

  const list = useQuery({
    queryKey: ['users'],
    queryFn: async () => (await api.get<StaffUser[]>('/api/users/')).data,
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

  return (
    <div className="space-y-8">
      <section>
        <h2 className="mb-4 text-xl font-semibold text-slate-900">Alta de staff</h2>
        <Card>
          <form
            onSubmit={handleSubmit((v) => create.mutate(v))}
            className="grid grid-cols-1 gap-4 md:grid-cols-2"
            noValidate
          >
            <div>
              <Label htmlFor="email">Correo</Label>
              <Input id="email" type="email" {...register('email')} />
              <FormError message={errors.email?.message} />
            </div>
            <div>
              <Label htmlFor="full_name">Nombre completo</Label>
              <Input id="full_name" {...register('full_name')} />
              <FormError message={errors.full_name?.message} />
            </div>
            <div>
              <Label htmlFor="position">Puesto</Label>
              <Input id="position" placeholder="Recepcionista, chef, …" {...register('position')} />
            </div>
            <div>
              <Label htmlFor="department">Departamento</Label>
              <Input
                id="department"
                placeholder="Front office, A&B, …"
                {...register('department')}
              />
            </div>
            <div className="md:col-span-2">
              <Button type="submit" disabled={isSubmitting || create.isPending}>
                {create.isPending ? <Spinner /> : 'Crear staff'}
              </Button>
            </div>
          </form>
        </Card>
        {alert && (
          <div className="mt-4">
            <Alert kind={alert.kind}>{alert.msg}</Alert>
          </div>
        )}
      </section>

      <section>
        <h2 className="mb-4 text-xl font-semibold text-slate-900">Staff registrado</h2>
        {list.isLoading && <p className="text-slate-500">Cargando…</p>}
        {list.isError && <Alert kind="error">{extractApiError(list.error)}</Alert>}
        {list.data && list.data.length === 0 && (
          <Alert kind="info">Aún no hay staff registrado.</Alert>
        )}
        {list.data && list.data.length > 0 && (
          <Card className="overflow-x-auto p-0">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-left text-slate-600">
                <tr>
                  <th className="px-4 py-3">Nombre</th>
                  <th className="px-4 py-3">Correo</th>
                  <th className="px-4 py-3">Puesto</th>
                  <th className="px-4 py-3">Departamento</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {list.data.map((u) => (
                  <tr key={u.id}>
                    <td className="px-4 py-3 font-medium text-slate-900">{u.full_name}</td>
                    <td className="px-4 py-3 text-slate-600">{u.email}</td>
                    <td className="px-4 py-3 text-slate-600">{u.position ?? '—'}</td>
                    <td className="px-4 py-3 text-slate-600">{u.department ?? '—'}</td>
                    <td className="px-4 py-3 text-right">
                      <Button
                        variant="danger"
                        className="h-8 px-3"
                        onClick={() => remove.mutate(u.id)}
                        disabled={remove.isPending}
                      >
                        Eliminar
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        )}
      </section>
    </div>
  );
};
