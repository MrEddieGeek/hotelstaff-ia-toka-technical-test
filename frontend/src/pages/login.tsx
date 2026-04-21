import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate } from 'react-router-dom';
import { z } from 'zod';

import { api, extractApiError } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Alert, Button, Card, FormError, Input, Label, Spinner } from '@/components/ui';

const schema = z.object({
  email: z.string().email('Correo inválido'),
  password: z.string().min(8, 'Mínimo 8 caracteres'),
});
type LoginForm = z.infer<typeof schema>;

export const LoginPage = () => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({ resolver: zodResolver(schema) });
  const [error, setError] = useState<string | null>(null);
  const setSession = useAuth((s) => s.setSession);
  const navigate = useNavigate();

  const onSubmit = async (values: LoginForm) => {
    setError(null);
    try {
      const { data } = await api.post('/api/auth/login', values);
      setSession({
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        user: { email: values.email },
      });
      navigate('/staff');
    } catch (err) {
      setError(extractApiError(err));
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <Card className="w-full max-w-md">
        <h1 className="mb-1 text-2xl font-semibold text-slate-900">HotelStaffIA</h1>
        <p className="mb-6 text-sm text-slate-600">
          Inicia sesión para gestionar staff del hotel y consultar al agente IA.
        </p>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
          <div>
            <Label htmlFor="email">Correo</Label>
            <Input id="email" type="email" autoComplete="email" {...register('email')} />
            <FormError message={errors.email?.message} />
          </div>
          <div>
            <Label htmlFor="password">Contraseña</Label>
            <Input
              id="password"
              type="password"
              autoComplete="current-password"
              {...register('password')}
            />
            <FormError message={errors.password?.message} />
          </div>
          {error && <Alert kind="error">{error}</Alert>}
          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? <Spinner /> : 'Ingresar'}
          </Button>
        </form>
      </Card>
    </div>
  );
};
