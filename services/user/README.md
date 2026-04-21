# user-service

Servicio de gestión de usuarios del sistema HotelStaffIA.

## Responsabilidades
- CRUD de usuarios (perfil, contacto, hotel asignado, fecha de alta).
- Publicación de eventos de dominio: `user.created`, `user.updated`, `user.deleted`.
- Validación local del JWT emitido por `auth-service` (JWKS).

## Desarrollo local

```bash
docker compose up -d postgres rabbitmq
cd services/user
pip install -e ".[dev]" ../../libs/hotelstaff_shared
uvicorn app.main:app --reload --port 8000
```

## Tests

```bash
pytest --cov=app --cov-report=term-missing
```

## Endpoints principales (pendientes de implementar en E2)

- `GET /users`, `GET /users/{id}`
- `POST /users`
- `PATCH /users/{id}`, `DELETE /users/{id}`
- `GET /health/live`, `GET /health/ready`
