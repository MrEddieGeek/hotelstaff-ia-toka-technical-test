import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import { api, extractApiError } from '@/lib/api';
import {
  Alert,
  Badge,
  Input,
  Label,
  SectionHeader,
  Surface,
} from '@/components/ui';

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

  const items = logs.data?.items ?? [];

  return (
    <div className="space-y-10">
      <SectionHeader
        eyebrow="Trazabilidad"
        title="Auditoría"
        meta={
          logs.data && (
            <span>
              {logs.data.total.toLocaleString('es-MX')} eventos en total
            </span>
          )
        }
      >
        Eventos de dominio publicados por los microservicios. Filtra por tipo
        para acotar el flujo.
      </SectionHeader>

      <div className="max-w-md">
        <Label htmlFor="event_type">Filtro por tipo</Label>
        <Input
          id="event_type"
          placeholder="user.created, auth.login.failed, …"
          value={eventType}
          onChange={(e) => setEventType(e.target.value.trim())}
        />
      </div>

      {logs.isLoading && <p className="text-sm text-muted-foreground">Cargando eventos…</p>}
      {logs.isError && <Alert kind="error">{extractApiError(logs.error)}</Alert>}
      {logs.data && items.length === 0 && (
        <Surface className="p-8 text-center">
          <p className="font-display text-lg text-foreground">Sin eventos</p>
          <p className="mx-auto mt-1 max-w-sm text-sm text-muted-foreground">
            {eventType
              ? `Ningún evento coincide con “${eventType}”. Prueba otro filtro o vacíalo.`
              : 'Crea o elimina staff para que los productores empiecen a publicar eventos.'}
          </p>
        </Surface>
      )}

      {items.length > 0 && (
        <>
          {/* Mobile: stacked */}
          <ul className="space-y-3 md:hidden">
            {items.map((l) => (
              <Surface key={l.event_id} as="article" className="p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-mono text-sm font-medium text-foreground">
                      {l.event_type}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(l.occurred_at).toLocaleString('es-MX')}
                    </p>
                  </div>
                  <Badge>{l.producer}</Badge>
                </div>
                <details className="mt-3 text-xs">
                  <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
                    Ver payload
                  </summary>
                  <pre className="mt-2 overflow-x-auto rounded bg-muted p-3 font-mono text-2xs text-muted-foreground">
                    {JSON.stringify(l.payload, null, 2)}
                  </pre>
                </details>
              </Surface>
            ))}
          </ul>

          {/* Desktop: table */}
          <div className="hidden overflow-hidden rounded-lg border border-border md:block">
            <table className="w-full text-sm">
              <thead className="bg-muted/60 text-left text-2xs font-semibold uppercase tracking-wider text-muted-foreground">
                <tr>
                  <th scope="col" className="px-4 py-3">
                    Fecha
                  </th>
                  <th scope="col" className="px-4 py-3">
                    Evento
                  </th>
                  <th scope="col" className="px-4 py-3">
                    Productor
                  </th>
                  <th scope="col" className="px-4 py-3">
                    Payload
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border bg-surface align-top">
                {items.map((l) => (
                  <tr key={l.event_id} className="transition-colors hover:bg-muted/40">
                    <td className="whitespace-nowrap px-4 py-3 text-muted-foreground">
                      {new Date(l.occurred_at).toLocaleString('es-MX')}
                    </td>
                    <td className="px-4 py-3 font-mono font-medium text-foreground">
                      {l.event_type}
                    </td>
                    <td className="px-4 py-3">
                      <Badge>{l.producer}</Badge>
                    </td>
                    <td className="px-4 py-3">
                      <details>
                        <summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground">
                          {Object.keys(l.payload).length} campos
                        </summary>
                        <pre className="mt-2 max-w-xl overflow-x-auto rounded bg-muted p-3 font-mono text-2xs text-muted-foreground">
                          {JSON.stringify(l.payload, null, 2)}
                        </pre>
                      </details>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};
