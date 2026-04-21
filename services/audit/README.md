# audit-service

Servicio de auditoría basado en eventos para HotelStaffIA.

## Responsabilidades
- Consume eventos de dominio desde RabbitMQ (topic `hotelstaff.events`).
- Persiste registros append-only en MongoDB con correlación por `event_id` (idempotencia).
- Expone API de consulta con filtros temporales y por entidad.

## Desarrollo local

```bash
docker compose up -d mongodb rabbitmq
cd services/audit
pip install -e ".[dev]" ../../libs/hotelstaff_shared
uvicorn app.main:app --reload --port 8000
```

## Tests

```bash
pytest --cov=app --cov-report=term-missing
```

## Endpoints principales (pendientes de implementar en E2)

- `GET /audit?entity=user&from=...&to=...`
- `GET /audit/{event_id}`
- `GET /health/live`, `GET /health/ready`

## Colecciones MongoDB

- `events` — documentos con `event_id` (único), `event_type`, `occurred_at`, `producer`, `payload`.
