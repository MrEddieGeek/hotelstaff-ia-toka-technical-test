import { NavLink, Outlet, useNavigate } from 'react-router-dom';

import { cn } from '@/lib/utils';
import { useAuth } from '@/store/auth';
import { Button } from '@/components/ui';

const navItems = [
  { to: '/staff', label: 'Staff' },
  { to: '/roles', label: 'Roles' },
  { to: '/audit', label: 'Auditoría' },
  { to: '/agent', label: 'Agente IA' },
];

export const Layout = () => {
  const { user, clear } = useAuth();
  const navigate = useNavigate();

  const logout = () => {
    clear();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-8">
            <h1 className="text-lg font-semibold text-slate-900">HotelStaffIA</h1>
            <nav className="flex gap-1">
              {navItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    cn(
                      'rounded-md px-3 py-2 text-sm font-medium',
                      isActive ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-100',
                    )
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <span className="text-slate-600">{user?.email}</span>
            <Button variant="ghost" onClick={logout}>
              Cerrar sesión
            </Button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
};
