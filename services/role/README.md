# role-service

Gestión de roles y permisos (RBAC) para HotelStaffIA.

## Responsabilidades
- CRUD de roles (ej. `admin`, `recepcion`, `housekeeping`, `restaurante`).
- Asignación y revocación de roles a usuarios.
- Publicación de eventos `role.assigned` y `role.revoked`.
- Validación local del JWT emitido por `auth-service`.

## Desarrollo local

```bash
docker compose up -d postgres rabbitmq
cd services/role
pip install -e ".[dev]" ../../libs/hotelstaff_shared
uvicorn app.main:app --reload --port 8000
```

## Tests

```bash
pytest --cov=app --cov-report=term-missing
```

## Endpoints principales (pendientes de implementar en E2)

- `GET /roles`, `POST /roles`, `DELETE /roles/{id}`
- `POST /users/{user_id}/roles/{role_id}` (asignar)
- `DELETE /users/{user_id}/roles/{role_id}` (revocar)
- `GET /health/live`, `GET /health/ready`
