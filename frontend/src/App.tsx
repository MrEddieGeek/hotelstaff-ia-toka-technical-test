import { Navigate, Route, Routes } from 'react-router-dom';

import { Layout } from '@/components/layout';
import { ProtectedRoute } from '@/components/protected-route';
import { AgentPage } from '@/pages/agent';
import { AuditPage } from '@/pages/audit';
import { LoginPage } from '@/pages/login';
import { RolesPage } from '@/pages/roles';
import { StaffPage } from '@/pages/staff';

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/staff" replace />} />
          <Route path="/staff" element={<StaffPage />} />
          <Route path="/roles" element={<RolesPage />} />
          <Route path="/audit" element={<AuditPage />} />
          <Route path="/agent" element={<AgentPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
