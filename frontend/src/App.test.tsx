import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, beforeEach } from 'vitest';

import App from './App';
import { useAuth } from '@/store/auth';

const renderApp = (path = '/') => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[path]}>
        <App />
      </MemoryRouter>
    </QueryClientProvider>,
  );
};

describe('App', () => {
  beforeEach(() => {
    useAuth.getState().clear();
  });

  it('redirige a /login cuando no hay sesión', () => {
    renderApp('/staff');
    expect(screen.getByRole('heading', { name: /HotelStaffIA/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/correo/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/contraseña/i)).toBeInTheDocument();
  });

  it('valida el formulario de login', async () => {
    const user = userEvent.setup();
    renderApp('/login');
    await user.click(screen.getByRole('button', { name: /ingresar/i }));
    expect(await screen.findByText(/correo inválido/i)).toBeInTheDocument();
    expect(screen.getByText(/mínimo 8 caracteres/i)).toBeInTheDocument();
  });

  it('muestra el layout autenticado cuando hay token', () => {
    useAuth.getState().setSession({
      accessToken: 'tok',
      refreshToken: 'r',
      user: { email: 'admin@hotel.mx' },
    });
    renderApp('/staff');
    expect(screen.getByRole('heading', { name: /alta de staff/i })).toBeInTheDocument();
    expect(screen.getByText('admin@hotel.mx')).toBeInTheDocument();
  });
});
