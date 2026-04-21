import { Navigate, Outlet } from 'react-router-dom';

import { useAuth } from '@/store/auth';

export const ProtectedRoute = () => {
  const token = useAuth((s) => s.accessToken);
  if (!token) return <Navigate to="/login" replace />;
  return <Outlet />;
};
