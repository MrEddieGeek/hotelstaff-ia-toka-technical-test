# user-service

Servicio de gestión de usuarios (staff de hotel) de HotelStaffIA.

## Responsabilidades

- CRUD de usuarios (`/users`): crear, listar con paginación, obtener, actualizar, borrar.
- Publica eventos de dominio a RabbitMQ: `user.created`, `user.updated`, `user.deleted`.
- Validación de JWT opcional (habilitable con `AUTH_REQUIRED=true` y `JWT_PUBLIC_KEY_PATH`).

## Arquitectura

DDD + Clean Architecture (`domain/application/infrastructure/interfaces`). El puerto `EventPublisher` se resuelve a `RabbitMQPublisher` en producción o `NullEventPublisher` en tests / cuando RabbitMQ no está disponible (degradación elegante).

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/users` | Crea usuario (emite `user.created`). |
| GET | `/users?limit=&offset=` | Lista paginada. |
| GET | `/users/{id}` | Detalle. |
| PATCH | `/users/{id}` | Parche parcial (emite `user.updated`). |
| DELETE | `/users/{id}` | Baja (emite `user.deleted`). |
| GET | `/health/live` \| `/health/ready` | Sondas. |

## Variables de entorno

| Variable | Por defecto | |
|---|---|---|
| `DATABASE_URL` / `POSTGRES_*` | — | Conexión Postgres. |
| `RABBITMQ_URL` | `amqp://guest:guest@rabbitmq:5672/` | Broker. |
| `EVENTS_EXCHANGE` | `hotelstaff.events` | Exchange topic. |
| `EVENTS_ENABLED` | `true` | Apágalo para tests locales. |
| `JWT_PUBLIC_KEY_PATH` | — | Para validar tokens del auth-service. |
| `AUTH_REQUIRED` | `false` | Activa el guard JWT en endpoints mutantes. |

## Comandos

```bash
pytest --cov=app
ruff check . --fix
alembic upgrade head
uvicorn app.main:app --reload --port 8002
```
