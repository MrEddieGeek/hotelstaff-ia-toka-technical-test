# Estrategia de Prompt Engineering — ia-agent

Este documento describe la estrategia de prompting del microservicio `ia-agent` (RAG sobre Qdrant + LLM).

## 1. System prompt

Ubicación: `services/ia-agent/app/application/services.py` → `SYSTEM_PROMPT`.

```
Eres un asistente experto en recursos humanos de un hotel. Respondes de forma
breve y profesional usando únicamente la información del contexto proporcionado.
Si el contexto no contiene la respuesta, di honestamente que no tienes información
suficiente en lugar de inventarla.
```

**Decisiones de diseño:**

- **Rol específico** ("RRHH de hotel") para anclar el dominio y reducir alucinaciones genéricas.
- **Respuestas breves y profesionales** porque el consumidor es un gerente que escanea, no lee.
- **Anti-alucinación explícita**: el modelo debe admitir ignorancia antes que inventar. Es la regla más importante y por eso va al final, donde los LLM le dan más peso.
- **Idioma implícito**: el prompt está en español y los documentos indexados también; el modelo responde en español por consistencia lingüística sin necesidad de instrucción explícita.

## 2. Plantilla de user prompt

```
Contexto:
{chunks recuperados por RAG, separados por saltos de línea dobles}

Pregunta: {pregunta del usuario}
```

**Por qué así:**

- Contexto **primero**, pregunta **al final**: los LLMs atienden mejor la información más reciente en la ventana.
- Separador visual claro (`\n\n`) entre chunks para que el modelo los perciba como documentos independientes y no como un solo bloque ruidoso.
- Sin few-shot examples: el dominio es suficientemente simple (Q&A sobre staff) y los ejemplos añaden tokens sin mejora medible en este caso de uso.

## 3. Pipeline RAG

1. **Embedding de la pregunta** con el mismo modelo que se usó para indexar (OpenAI `text-embedding-3-small` o `DeterministicEmbeddings` 384-dim en fallback).
2. **Búsqueda top-k** (default `k=4`) por similitud coseno en Qdrant.
3. **Construcción del contexto** concatenando el `text` de cada chunk recuperado. No reordenamos por score (ya vienen ordenados) ni reescribimos.
4. **Llamada al LLM** con `temperature=0.2` (respuestas deterministas, no creativas) y sin `top_p` customizado.

## 4. Chain-of-thought

**No se usa** explícitamente. El caso de uso (responder "¿quién es recepcionista?") no se beneficia de razonamiento paso-a-paso y CoT incrementaría latencia y tokens sin mejorar calidad. Si en el futuro se añadieran consultas analíticas ("¿qué departamento tiene menos personal activo?"), se añadiría un prompt alternativo con CoT.

## 5. Evaluación de respuestas

Implementada parcialmente:

| Métrica | Dónde | Estado |
|---|---|---|
| **Latencia end-to-end** | Medida en frontend (`src/pages/agent.tsx`) con `performance.now()` y mostrada al usuario | ✅ |
| **Logs estructurados** del ask | `structlog` en `AgentService.ask` propaga `request_id` | ✅ |
| **Tokens in/out y coste** | Propuesta: instrumentar `response.usage` de OpenAI en `OpenAILLM.complete` y loguearlo | ⏳ Pendiente (ver sección 7) |
| **Validación de calidad** | Revisión manual sobre logs de `question + sources + answer` | 🟡 Proceso manual documentado |
| **Score de retrieval** | Devuelto por `/agent/ask` en `sources[].score` para trazabilidad | ✅ |

### Script sugerido para evaluación offline

```python
# Pseudocódigo para scripts/eval_agent.py (fuera de alcance de esta entrega)
questions = load_gold_set("eval/questions.jsonl")  # {question, expected_doc_ids}
for q in questions:
    r = client.post("/agent/ask", json=q)
    recall_at_k = len(set(r["sources"]) & set(q["expected_doc_ids"])) / len(q["expected_doc_ids"])
    latency_ms = r["latency_ms"]
    log(q, recall_at_k, latency_ms)
```

Las métricas de interés son **recall@k** (¿recupera los documentos correctos?) y **p95 de latencia**. La calidad textual de la respuesta se evalúa con LLM-as-a-judge o revisión humana.

## 6. Manejo de errores y rate limiting

- **Timeouts**: `httpx` con timeout implícito del cliente de OpenAI (~60s). Propuesta: reducir a 15s con circuit breaker.
- **429 de OpenAI**: actualmente propagado al cliente como 500. Mejora futura: capturar `openai.RateLimitError`, respetar `Retry-After`, y si se agota el presupuesto de reintentos, **fallback a `StubLLM`** devolviendo las fuentes recuperadas sin generación (mantiene valor de búsqueda).
- **`StubLLM` como red de seguridad**: configurable con `LLM_PROVIDER=stub`, extrae el contexto y lo devuelve. Siempre disponible, sin costes ni latencia externa. Se usa también en tests.

## 7. Optimización de costes

Acciones implementadas:

- `top_k=4` por defecto (no 10) → contexto corto.
- `temperature=0.2` para permitir caching de respuestas idénticas en el futuro.
- `gpt-4o-mini` como default, no `gpt-4o` (coste 10× menor).
- Embeddings `text-embedding-3-small` (coste ~5× menor que `-large`).

Acciones propuestas (no implementadas):

- Caché de embeddings de preguntas frecuentes en Redis (la pregunta "¿quiénes son recepcionistas?" no debería pagar embedding 100 veces al día).
- Caché de respuestas para preguntas idénticas recientes (TTL corto, ej. 5 min) invalidado al recibir `user.updated`.
- Rate limit por usuario en el BFF para `/api/agent/*` (actualmente sólo por IP).
- Dashboard de tokens/día por endpoint con alertas en desviaciones.
