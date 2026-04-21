import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';

import { api, extractApiError } from '@/lib/api';
import { Alert, Button, Card, Input, Label, Spinner } from '@/components/ui';

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

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Agente IA</h2>
        <p className="mt-1 text-sm text-slate-600">
          Pregunta en lenguaje natural sobre el staff del hotel. Las respuestas se construyen con
          RAG sobre la base vectorial indexada desde los eventos <code>user.created</code>.
        </p>
      </div>

      <Card>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (question.trim()) {
              setResponse(null);
              ask.mutate();
            }
          }}
          className="space-y-4"
        >
          <div>
            <Label htmlFor="question">Pregunta</Label>
            <Input
              id="question"
              placeholder="¿Quiénes son los recepcionistas del turno matutino?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              required
            />
          </div>
          <Button type="submit" disabled={ask.isPending || !question.trim()}>
            {ask.isPending ? <Spinner /> : 'Preguntar'}
          </Button>
        </form>
      </Card>

      {ask.isError && <Alert kind="error">{extractApiError(ask.error)}</Alert>}

      {response && (
        <Card>
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-900">Respuesta</h3>
            {latencyMs !== null && (
              <span className="text-xs text-slate-500">{latencyMs} ms</span>
            )}
          </div>
          <p className="whitespace-pre-wrap text-slate-800">{response.answer}</p>

          {response.sources.length > 0 && (
            <>
              <h4 className="mt-6 mb-2 text-sm font-semibold text-slate-700">
                Fuentes recuperadas
              </h4>
              <ul className="space-y-2">
                {response.sources.map((s) => (
                  <li key={s.doc_id} className="rounded border border-slate-200 p-3 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs text-slate-500">{s.doc_id}</span>
                      <span className="text-xs text-slate-500">
                        score {s.score.toFixed(3)}
                      </span>
                    </div>
                    <p className="mt-1 text-slate-700">{s.text}</p>
                  </li>
                ))}
              </ul>
            </>
          )}
        </Card>
      )}
    </div>
  );
};
