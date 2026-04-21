# Ejercicio 4 — Desempeño bajo presión: diagnóstico de incidente

**Escenario reportado:** los usuarios no pueden guardar registros, varios microservicios devuelven 500 intermitentes y hay reportes de alta latencia en las respuestas del agente de IA.

Este documento describe cómo abordaría el incidente en el sistema HotelStaffIA (BFF + auth/user/role/audit/ia-agent + Postgres/Mongo/Redis/RabbitMQ/Qdrant) desde el minuto cero hasta la estabilización.

---

## 1. Los primeros 5 minutos: confirmar alcance y frenar la sangría

Antes de teorizar, necesito saber **qué está roto y para cuántos**. En paralelo:

1. **Confirmar en el frontend real** (no sólo reportes): intento guardar un `POST /api/users` con una cuenta de prueba. Si falla con 500, el problema es real y no sólo percepción.
2. **Healthchecks agregados:** `GET /health/ready` de BFF, auth, user, role, audit e ia-agent. Cualquier 503 ya me da un candidato.
3. **Tráfico y tasa de error** en los logs del BFF (pino JSON). Un `jq 'select(.res.statusCode >= 500)'` sobre los últimos 10 min me dice qué rutas fallan y en qué proporción.
4. **Declarar el incidente** en el canal correspondiente con severidad provisional (SEV-2 si la escritura de usuarios está caída, SEV-3 si es sólo la IA) y asignar scribe + commander. Stakeholders se enteran **ahora**, no al final.
5. **Mitigación inmediata disponible**: si el ia-agent es el único afectado y está tumbando latencia aguas arriba, desactivar temporalmente su consumer (`CONSUMER_ENABLED=false`) y marcar el panel de IA como "mantenimiento" en la UI. Lo importante es que el CRM no se caiga por un problema de un componente accesorio.

**Principio:** priorizo frenar el daño de usuario sobre entender la causa raíz. El diagnóstico puede esperar 10 minutos; los usuarios enojados no.

---

## 2. Hipótesis ordenadas por probabilidad × impacto

Con la arquitectura actual, estas son las causas típicas — ordenadas por lo que **más frecuentemente** produce este patrón (500s en escritura + latencia IA):

| # | Hipótesis | Señal que la confirma | Coste de verificación |
|---|-----------|-----------------------|-----------------------|
| 1 | **Postgres saturado / pool agotado** (user/auth/role comparten instancia) | `TimeoutError: QueuePool limit` en logs, `pg_stat_activity` con conexiones idle in transaction | bajo |
| 2 | **RabbitMQ caído o con colas atascadas** → `user-service` bloqueado publicando `user.created` | logs `publisher.unavailable`, queue depth > umbral en `audit` e `ia-agent` | bajo |
| 3 | **Rate limit de OpenAI/Gemini** saturando el ia-agent, que encadena timeouts al BFF si el cliente espera | HTTP 429 del proveedor en logs, tokens/s en límite, latencia p99 del `/agent/ask` > 30s | medio |
| 4 | **Qdrant lento o sin colección**: el embedding sube, la búsqueda se cuelga | errores en `vector_store.search`, CPU de Qdrant al 100% | bajo |
| 5 | **Expiración/rotación de la clave JWT** → BFF rechaza tokens válidos y devuelve 401 que un cliente mal instrumentado reporta como "no puedo guardar" | pico de 401 en BFF, JWKS devolviendo kid distinto al del token | bajo |
| 6 | **Migración Alembic a medias** (un pod pasó, otro no) en user/auth | 500 con `UndefinedColumn` en logs | bajo |
| 7 | **Red interna docker / DNS** entre BFF y microservicios | `ECONNREFUSED`/`ETIMEDOUT` en `bff.forward.upstream_error` | bajo |
| 8 | **Fallo en cascada**: audit-service caído → si estuviera en path síncrono bloquearía. En nuestro diseño **no lo está** (es consumer async), pero lo verifico para descartar | cola `audit.events` con depth creciente, sin consumers | bajo |
| 9 | **Fuga de memoria en un servicio Python** tras un deploy reciente | RSS creciente en `docker stats`, OOMKilled en `docker ps -a` | medio |

> La hipótesis 3 (IA) suele ser causa *acompañante*, rara vez la raíz de 500s de escritura. Es tentador culpar a la IA porque está "caliente", pero hay que resistir el sesgo.

---

## 3. Plan de diagnóstico sistemático

### 3.1. Correlación por request

Cada request atraviesa BFF → microservicio → (RabbitMQ) con el mismo `x-request-id`. El flujo es:

1. Tomo un `request_id` de un error 500 reciente en el BFF.
2. Busco ese `reqId` en los logs de **todos** los microservicios (`docker compose logs | grep <reqId>`). Esto me da la traza completa: dónde se detuvo, qué excepción se lanzó, cuánto tardó cada salto.
3. Con logs estructurados JSON puedo agregar: `jq 'select(.reqId=="X") | {svc, time, level, msg, error}'`.

### 3.2. Métricas de infraestructura (lectura rápida)

- `docker stats` → CPU/mem de cada contenedor. Un servicio al 100% de CPU con otros al 5% es diagnóstico.
- Postgres: `SELECT count(*), state FROM pg_stat_activity GROUP BY state;` — si hay muchos `idle in transaction` la app no está cerrando transacciones.
- RabbitMQ Management UI (15672): depth por cola, tasa de publicación vs consumo, conexiones activas.
- Qdrant: `GET /collections/hotelstaff_users` → status y vectores indexados.
- Redis: `redis-cli info stats` → `instantaneous_ops_per_sec`, `used_memory`.

### 3.3. Verificar cada hipótesis (en el orden de la tabla)

Para cada una, la pregunta binaria que zanja: *"¿los logs/métricas confirman este patrón o no?"*. Si no, siguiente. Evito quedarme atascado debuggeando una teoría sin evidencia por más de 10 min.

### 3.4. Reproducción controlada

Si los logs son ambiguos, lanzo carga sintética:

- Un loop de `POST /api/auth/login` + `POST /api/users` con 20 req/s durante 1 min. Si reproduce el 500, tengo banco de pruebas.
- `POST /api/agent/ask` con questions conocidas y `top_k=4` para medir latencia base del RAG y aislar si el problema es embeddings, Qdrant, o LLM.

---

## 4. Problemas específicos del agente IA

Merecen párrafo aparte porque el patrón es diferente al de un microservicio CRUD:

### Latencia

- **Causa frecuente #1:** request con `max_tokens` alto + contexto largo. Mitigación: truncar contexto recuperado a 2–3 chunks top-k, no 10.
- **Causa frecuente #2:** `OpenAI` con reintentos implícitos encima de un 429 ya fallido. Mitigación: timeout agresivo (10–15s) + circuit breaker que apague el `/agent/ask` y devuelva "servicio temporalmente no disponible" en vez de colgar al cliente.

### Coste de tokens

- Instrumentar `usage.prompt_tokens` + `usage.completion_tokens` por request en logs estructurados.
- Dashboard simple con **tokens/día por endpoint**. Un pico de 10× sobre la línea base suele ser: (a) un loop del frontend disparando `/agent/ask` en cada render, (b) un chunk enorme indexado que inflando el contexto.
- Alertar en tokens/hora, no sólo en errores. El coste es un modo de falla silencioso.

### Rate limiting

- Del lado del proveedor: 429 + cabecera `Retry-After`. Respetarla (exponential backoff con jitter), no reintentar ciegamente.
- Del lado nuestro: rate limit por usuario en el BFF para `/api/agent/*` — un usuario no debería poder quemar el presupuesto del tenant.
- **Fallback degradado:** si 3 requests seguidas al LLM fallan, responder con `StubLLM` ("No puedo generar una respuesta en este momento, aquí están los documentos más relevantes:") + las fuentes recuperadas por RAG. El usuario **sigue obteniendo valor** aunque el LLM esté caído.

### Calidad de respuesta

- Log de cada ask con `{question, retrieved_doc_ids, scores, answer, latency, tokens}`.
- Revisión manual semanal de 20 muestras aleatorias + 20 con score de retrieval < 0.5 → suelen exponer problemas de embeddings o gaps en el corpus.

---

## 5. Comunicación con stakeholders

Patrón que funciona: **una actualización cada 15 min aunque no haya novedad**. El silencio genera más ruido que una nota diciendo "seguimos investigando".

Formato:

```
[INCIDENTE #142 — 16:05 UTC] Actualización 2/N

Estado: investigando
Impacto: usuarios no pueden crear staff nuevo (p95 500s). Login y consulta funcionan.
Mitigación aplicada: panel de agente IA deshabilitado preventivamente.
Hipótesis principal: saturación del pool de Postgres en user-service.
Próximo check-in: 16:20.
Commander: @edgar · Scribe: @persona-2
```

Al cerrar el incidente:

1. **Confirmación de estabilidad** con métricas (5 min sin 500s, p95 vuelto a baseline).
2. **Post-mortem blameless** en 48h con: timeline, causa raíz, por qué la detección tardó lo que tardó, acciones de prevención (no de castigo).
3. **Items accionables con dueño y fecha** — no aceptar "mejorar monitoreo" como action item; exigir "añadir alerta en pool_size > 80% con dueño @X y fecha Y".

---

## 6. Qué dejaría instrumentado para la próxima

Las incidencias revelan lo que faltaba:

- Métricas de pool de DB expuestas por cada servicio FastAPI.
- Traza distribuida (OpenTelemetry) — por ahora tenemos `x-request-id` manual, suficiente para este tamaño pero limitante a medida que crezca.
- Alertas en: tasa de 5xx por servicio, queue depth de RabbitMQ, latencia p95 de `/agent/ask`, tokens/hora, ratio de 429 de OpenAI.
- Runbook versionado con los comandos concretos de la sección 3 para que cualquier on-call pueda ejecutarlos sin pensar.

---

## 7. Resumen ejecutivo (1 párrafo)

Frente al patrón "500s al guardar + alta latencia IA" mi aproximación es: **contener primero** (deshabilitar IA si está sospechosa, declarar incidente), **diagnosticar por correlación de `request_id`** atravesando BFF y microservicios con logs JSON, **priorizar hipótesis de infra compartida** (Postgres, RabbitMQ) antes que las de IA porque es donde la probabilidad × impacto es mayor, **tratar el agente IA como un sistema con modos de falla propios** (latencia, tokens, rate limits) con fallback a RAG sin LLM, y **comunicar cada 15 minutos** con formato estructurado hasta el cierre y post-mortem blameless.
