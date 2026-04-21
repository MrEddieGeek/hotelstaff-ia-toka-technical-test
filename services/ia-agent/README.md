# ia-agent

Agente de IA con RAG (Retrieval-Augmented Generation) sobre Qdrant e integración con OpenAI/Gemini.

## Responsabilidades
- Consume eventos `user.*` para mantener el índice vectorial fresco.
- Expone endpoints de consulta en lenguaje natural sobre usuarios/roles del sistema.
- Ejecuta pipeline de embeddings y recuperación por similitud coseno.
- Métricas por request: latencia, tokens in/out, coste estimado.

## Desarrollo local

```bash
docker compose up -d qdrant rabbitmq
cd services/ia-agent
pip install -e ".[dev]" ../../libs/hotelstaff_shared
export OPENAI_API_KEY=sk-...
uvicorn app.main:app --reload --port 8000
```

## Tests

```bash
pytest --cov=app --cov-report=term-missing
```

## Endpoints principales (pendientes de implementar en E5)

- `POST /agent/query` — consulta RAG en lenguaje natural
- `POST /agent/reindex` — reconstruye el índice desde user-service
- `GET /agent/metrics` — métricas agregadas (latencia, tokens, coste)
- `GET /health/live`, `GET /health/ready`

## Proveedor LLM

Abstraído detrás de `LLMProvider`. Implementaciones: `OpenAIProvider`, `GeminiProvider`. Cambio vía `LLM_PROVIDER=openai|gemini`.
