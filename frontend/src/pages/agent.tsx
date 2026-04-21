import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';

import { api, extractApiError } from '@/lib/api';
import {
  Alert,
  Badge,
  Button,
  Label,
  SectionHeader,
  Spinner,
  Surface,
  Textarea,
} from '@/components/ui';

interface Source {
  doc_id: string;
  text: string;
  score: number;
  metadata: Record<string, unknown>;
}

interface AskResponse {
  answer: string;
  sources: Source[];
}

const formatLatency = (ms: number) =>
  ms >= 1000 ? `${(ms / 1000).toFixed(2)} s` : `${ms} ms`;

export const AgentPage = () => {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState<AskResponse | null>(null);
  const [latencyMs, setLatencyMs] = useState<number | null>(null);

  const ask = useMutation({
    mutationFn: async () => {
      const started = performance.now();
      const { data } = await api.post<AskResponse>('/api/agent/ask', {
        question,
        top_k: 4,
      });
      setLatencyMs(Math.round(performance.now() - started));
      return data;
    },
    onSuccess: (data) => setResponse(data),
  });

  const submit = () => {
    if (!question.trim() || ask.isPending) return;
    setResponse(null);
    ask.mutate();
  };

  return (
    <div className="space-y-10">
      <SectionHeader eyebrow="RAG" title="Agente">
        Pregunta en lenguaje natural sobre el staff. La respuesta se construye
        recuperando fragmentos de la base vectorial.
      </SectionHeader>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          submit();
        }}
        className="space-y-3"
      >
        <Label htmlFor="question">Tu pregunta</Label>
        <div className="relative">
          <Textarea
            id="question"
            rows={3}
            placeholder="¿Quiénes son los recepcionistas del turno matutino?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') submit();
            }}
            required
            className="pr-32"
          />
          <div className="absolute bottom-2.5 right-2.5">
            <Button
              type="submit"
              size="sm"
              disabled={ask.isPending || !question.trim()}
            >
              {ask.isPending ? <Spinner /> : 'Preguntar'}
            </Button>
          </div>
        </div>
        <p className="text-xs text-muted-foreground">
          ⌘/Ctrl + Enter para enviar.
        </p>
      </form>

      {ask.isError && <Alert kind="error">{extractApiError(ask.error)}</Alert>}

      {ask.isPending && (
        <Surface className="p-6">
          <p className="text-sm text-muted-foreground">
            Recuperando fragmentos relevantes y redactando respuesta…
          </p>
          <div className="mt-4 space-y-2">
            <div className="h-3 w-11/12 animate-pulse rounded bg-muted" />
            <div className="h-3 w-9/12 animate-pulse rounded bg-muted" />
            <div className="h-3 w-7/12 animate-pulse rounded bg-muted" />
          </div>
        </Surface>
      )}

      {response && (
        <article className="grid gap-6 lg:grid-cols-[minmax(0,1.6fr)_minmax(280px,1fr)]">
          <Surface className="p-6 lg:p-8">
            <header className="flex items-baseline justify-between gap-4 border-b border-border pb-4">
              <h3 className="font-display text-xl font-medium text-foreground">
                Respuesta
              </h3>
              {latencyMs !== null && (
                <p className="text-2xs uppercase tracking-wider text-muted-foreground">
                  Generada en{' '}
                  <span className="font-mono text-foreground">
                    {formatLatency(latencyMs)}
                  </span>{' '}
                  · {response.sources.length} fuentes
                </p>
              )}
            </header>
            <p className="mt-5 whitespace-pre-wrap text-base leading-relaxed text-foreground">
              {response.answer}
            </p>
          </Surface>

          <aside aria-labelledby="fuentes" className="space-y-3">
            <h4
              id="fuentes"
              className="text-2xs font-semibold uppercase tracking-wider text-muted-foreground"
            >
              Fuentes recuperadas
            </h4>
            {response.sources.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                Sin coincidencias en el índice.
              </p>
            ) : (
              <ol className="space-y-2.5">
                {response.sources.map((s, i) => (
                  <li key={s.doc_id}>
                    <Surface className="p-3.5">
                      <div className="flex items-baseline justify-between gap-2">
                        <span className="font-mono text-2xs text-muted-foreground">
                          {String(i + 1).padStart(2, '0')} · {s.doc_id}
                        </span>
                        <Badge tone="accent">{s.score.toFixed(3)}</Badge>
                      </div>
                      <p className="mt-2 line-clamp-3 text-xs text-muted-foreground">
                        {s.text}
                      </p>
                    </Surface>
                  </li>
                ))}
              </ol>
            )}
          </aside>
        </article>
      )}

      {!ask.isPending && !response && !ask.isError && (
        <Surface className="p-8">
          <p className="font-display text-lg text-foreground">Pregunta para empezar</p>
          <p className="mt-1 max-w-md text-sm text-muted-foreground">
            El agente responde sobre el staff indexado desde los eventos{' '}
            <code className="font-mono text-foreground">user.created</code>.
            Empieza con algo como “lista de chefs” o “staff del departamento de A&amp;B”.
          </p>
        </Surface>
      )}
    </div>
  );
};
