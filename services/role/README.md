# role-service

Gestión de roles (RBAC) y asignación usuario↔rol para HotelStaffIA.

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/roles` | Crea un rol con permisos JSON. |
| GET | `/roles` | Lista roles. |
| POST | `/assignments` | Asigna rol a usuario (emite `role.assigned`). |
| DELETE | `/assignments?user_id=&role_id=` | Revoca (emite `role.revoked`). |
| GET | `/users/{user_id}/roles` | Lista asignaciones del usuario. |

## Datos

- `roles.roles` (id, name UNIQUE, description, permissions JSONB, created_at)
- `roles.user_roles` (user_id, role_id) PK compuesta; FK a roles.roles.

## Eventos publicados

`role.assigned` — `{user_id, role_id, role_name, permissions}`
`role.revoked` — `{user_id, role_id, role_name}`

## Comandos

```bash
pytest --cov=app
ruff check . --fix
alembic upgrade head
uvicorn app.main:app --reload --port 8003
```
