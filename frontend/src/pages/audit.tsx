import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import { api, extractApiError } from '@/lib/api';
import { Alert, Card, Input, Label } from '@/components/ui';

interface AuditLog {
  event_id: string;
  event_type: string;
  producer: string;
  occurred_at: string;
  payload: Record<string, unknown>;
}

interface AuditResponse {
  items: AuditLog[];
  total: number;
}

export const AuditPage = () => {
  const [eventType, setEventType] = useState('');

  const logs = useQuery({
    queryKey: ['audit', eventType],
    queryFn: async () => {
      const params = eventType ? { event_type: eventType, limit: 50 } : { limit: 50 };
      const { data } = await api.get<AuditResponse>('/api/audit/logs', { params });
      return data;
    },
  });

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-slate-900">Auditoría</h2>
      <Card>
        <Label htmlFor="event_type">Filtrar por tipo de evento</Label>
        <Input
          id="event_type"
          placeholder="user.created, auth.login.failed, …"
          value={eventType}
          onChange={(e) => setEventType(e.target.value)}
        />
      </Card>

      {logs.isLoading && <p className="text-slate-500">Cargando…</p>}
      {logs.isError && <Alert kind="error">{extractApiError(logs.error)}</Alert>}
      {logs.data && logs.data.items.length === 0 && (
        <Alert kind="info">No hay eventos registrados para este filtro.</Alert>
      )}
      {logs.data && logs.data.items.length > 0 && (
        <Card className="overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-slate-600">
              <tr>
                <th className="px-4 py-3">Fecha</th>
                <th className="px-4 py-3">Evento</th>
                <th className="px-4 py-3">Productor</th>
                <th className="px-4 py-3">Payload</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {logs.data.items.map((l) => (
                <tr key={l.event_id}>
                  <td className="px-4 py-3 text-slate-600">
                    {new Date(l.occurred_at).toLocaleString('es-MX')}
                  </td>
                  <td className="px-4 py-3 font-medium text-slate-900">{l.event_type}</td>
                  <td className="px-4 py-3 text-slate-600">{l.producer}</td>
                  <td className="px-4 py-3 font-mono text-xs text-slate-500">
                    {JSON.stringify(l.payload)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  );
};
