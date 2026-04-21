# ia-agent

Agente de IA con RAG (Retrieval-Augmented Generation) sobre Qdrant e integración con OpenAI, Gemini o un LLM stub determinista para desarrollo y pruebas.

## Responsabilidades

- Indexa documentos de staff (nombre, puesto, departamento) como embeddings en Qdrant.
- Consume eventos `user.created` y `user.updated` desde RabbitMQ para mantener el índice vectorial al día sin intervención manual.
- Responde preguntas en lenguaje natural combinando recuperación por similitud coseno (top-k) y generación con el LLM configurado.
- Ofrece degradación elegante: sin Qdrant usa un store en memoria, sin API keys usa `StubLLM`, sin RabbitMQ arranca sin consumer.

## Endpoints

- `POST /agent/index` — indexa un documento `{doc_id, text, metadata}`.
- `POST /agent/index/bulk` — indexa una lista de documentos.
- `POST /agent/ask` — `{question, top_k?}` → `{answer, sources[]}`.
- `GET /health/live` · `GET /health/ready`.

## Variables de entorno

| Variable | Default | Descripción |
|---|---|---|
| `LLM_PROVIDER` | `stub` | `openai`, `gemini` o `stub`. |
| `OPENAI_API_KEY` / `OPENAI_MODEL` / `OPENAI_EMBEDDING_MODEL` | — | Credenciales y modelos OpenAI. |
| `GEMINI_API_KEY` / `GEMINI_MODEL` | — | Credenciales y modelo Gemini. |
| `QDRANT_URL` | `http://qdrant:6333` | Endpoint Qdrant. |
| `QDRANT_COLLECTION` | `hotelstaff_users` | Colección vectorial. |
| `USE_MEMORY_VECTOR_STORE` | `false` | Fuerza store en memoria (tests / dev sin Qdrant). |
| `RABBITMQ_URL` / `EVENTS_EXCHANGE` / `EVENTS_QUEUE` | — | Consumer de eventos de dominio. |
| `CONSUMER_ENABLED` | `true` | Desactiva el consumer en entornos de test. |

## Desarrollo local

```bash
docker compose up -d qdrant rabbitmq
cd services/ia-agent
pip install -e ".[dev]" ../../libs/hotelstaff_shared
export LLM_PROVIDER=openai OPENAI_API_KEY=sk-...
uvicorn app.main:app --reload --port 8000
```

## Tests

```bash
pytest --cov=app --cov-report=term-missing
```

Los tests usan `USE_MEMORY_VECTOR_STORE=true`, `LLM_PROVIDER=stub` y `CONSUMER_ENABLED=false`, por lo que no requieren Qdrant, RabbitMQ ni claves de API.

## Flujo RAG

1. `embeddings.embed(texts)` → vectores (OpenAI o hash determinista 384-dim).
2. `store.upsert(doc_id, vector, metadata)` en Qdrant o store en memoria.
3. En `/agent/ask`: se embebe la pregunta, se recuperan los top-k chunks, se construye el contexto y se pasa al `LLMProvider` junto al prompt de sistema.
4. La respuesta se devuelve con las fuentes (`doc_id`, `text`, `score`, `metadata`) para trazabilidad.
