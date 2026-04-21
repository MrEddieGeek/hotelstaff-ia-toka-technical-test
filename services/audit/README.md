# audit-service

Servicio de auditoría basado en eventos para HotelStaffIA. Consume todos los
eventos de dominio (`user.*`, `auth.*`, `role.*`) desde RabbitMQ y los persiste
en MongoDB como registro inmutable.

## Funcionamiento

```
[user|role|auth-service] ──event──► RabbitMQ (hotelstaff.events)
                                         │
                                         ▼
                                   [audit-service]
                                         │
                                         ▼
                                   MongoDB → audit_logs
```

El consumidor bindea la cola `audit.events` con routing keys `user.*`, `auth.*`, `role.*`. Los eventos se almacenan con índice único por `event_id` — la segunda vez que llega el mismo evento se ignora (**idempotencia**). Fallos de procesamiento van a la DLX declarada por `EventBus`.

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/audit?event_type=&limit=&offset=` | Consulta paginada de logs. |
| GET | `/health/live` \| `/health/ready` | Sondas. |

## Variables de entorno

| Variable | Por defecto | |
|---|---|---|
| `MONGO_URI` | `mongodb://mongodb:27017` | |
| `MONGO_DB` | `hotelstaff_audit` | |
| `USE_MONGOMOCK` | `false` | `true` en tests (mongomock-motor). |
| `RABBITMQ_URL` | `amqp://guest:guest@rabbitmq:5672/` | |
| `EVENTS_EXCHANGE` | `hotelstaff.events` | |
| `EVENTS_QUEUE` | `audit.events` | |
| `CONSUMER_ENABLED` | `true` | |

## Comandos

```bash
pytest --cov=app
ruff check . --fix
uvicorn app.main:app --reload --port 8004
```
