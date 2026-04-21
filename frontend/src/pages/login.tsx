import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate } from 'react-router-dom';
import { z } from 'zod';

import { api, extractApiError } from '@/lib/api';
import { useAuth } from '@/store/auth';
import { Alert, Button, FormError, Input, Label, Spinner } from '@/components/ui';

const schema = z.object({
  email: z.string().trim().toLowerCase().email('Correo inválido'),
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
    <main className="grid min-h-screen grid-rows-[1fr_auto] bg-background lg:grid-cols-[1.05fr_minmax(380px,0.95fr)] lg:grid-rows-1">
      <aside className="relative hidden overflow-hidden border-r border-border bg-surface lg:block">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_28%,var(--accent-soft),transparent_55%)] opacity-80" />
        <div className="relative flex h-full flex-col justify-between p-12">
          <div className="flex items-baseline gap-2">
            <span aria-hidden="true" className="h-2 w-2 rounded-full bg-accent" />
            <span className="font-display text-base font-medium tracking-tight">
              HotelStaff
            </span>
            <span className="text-base font-medium tracking-tight text-muted-foreground">
              IA
            </span>
          </div>
          <div className="max-w-md">
            <p className="text-2xs font-semibold uppercase tracking-wider text-accent-soft-foreground">
              Operación · Personal · IA
            </p>
            <p className="mt-3 font-display text-3xl font-medium leading-tight text-foreground">
              Gestiona el equipo del hotel con la calma de un buen turno.
            </p>
            <p className="mt-4 max-w-prose text-sm text-muted-foreground">
              Una sola consola para staff, roles, auditoría y consultas en lenguaje
              natural al agente.
            </p>
          </div>
          <p className="text-2xs uppercase tracking-wider text-muted-foreground">
            v0.1 · prueba técnica Toka
          </p>
        </div>
      </aside>

      <section className="flex items-center justify-center px-4 py-12 sm:px-8">
        <div className="w-full max-w-sm">
          <h1 className="font-display text-2xl font-medium text-foreground">
            Inicia sesión
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Acceso restringido al staff autorizado.
          </p>

          <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-5" noValidate>
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
              <Label htmlFor="password">Contraseña</Label>
              <Input
                id="password"
                type="password"
                autoComplete="current-password"
                aria-invalid={!!errors.password}
                {...register('password')}
              />
              <FormError message={errors.password?.message} />
            </div>
            {error && <Alert kind="error">{error}</Alert>}
            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? <Spinner /> : 'Ingresar'}
            </Button>
          </form>
        </div>
      </section>
    </main>
  );
};
