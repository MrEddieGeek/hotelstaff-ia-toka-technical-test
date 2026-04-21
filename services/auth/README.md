# auth-service

Servicio de autenticación y emisión de JWT (RS256) para HotelStaffIA.

## Responsabilidades
- Registro y login de usuarios del sistema.
- Emisión de **access tokens** (15 min) y **refresh tokens** (7 días).
- Exposición del **JWKS** público para validación distribuida.
- Publicación de eventos `auth.user_logged_in` y `auth.user_login_failed`.

## Desarrollo local

```bash
# Desde la raíz del monorepo
docker compose up -d postgres redis
cd services/auth
pip install -e ".[dev]" ../../libs/hotelstaff_shared
uvicorn app.main:app --reload --port 8000
```

## Tests

```bash
pytest --cov=app --cov-report=term-missing
```

## Endpoints principales

- `GET /health/live` — liveness
- `GET /health/ready` — readiness (incluye verificación de Postgres/Redis cuando se implemente)
- `POST /auth/register` — registrar usuario
- `POST /auth/login` — emitir par de tokens
- `POST /auth/refresh` — renovar access token
- `GET /.well-known/jwks.json` — claves públicas para validación

## Estructura (Clean Architecture)

```
app/
├── domain/           # Entidades y reglas de negocio puras
├── application/      # Casos de uso
├── infrastructure/   # Persistencia, mensajería, clientes externos
└── interfaces/       # Routers HTTP y consumers de eventos
```
