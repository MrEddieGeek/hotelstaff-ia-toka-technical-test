# auth-service

Servicio de autenticación y emisión de JWT para HotelStaffIA.

## Responsabilidades

- Registro de usuarios con hashing Argon2id.
- Login (`POST /auth/login` JSON y `POST /auth/token` OAuth2 password grant).
- Emisión de access + refresh tokens **JWT RS256** firmados con clave privada.
- Exposición de la clave pública vía **JWKS** (`GET /.well-known/jwks.json`) para validación distribuida.
- Validación del access token en `GET /auth/me`.

Única fuente de firma de tokens. El resto de servicios verifica localmente con la clave pública (cero acoplamiento en caliente con auth-service).

## Arquitectura (DDD + Clean Architecture)

```
app/
  domain/           # Entidades (User) + errores de dominio
  application/      # Casos de uso (AuthService) + DTOs + Ports
  infrastructure/   # SQLAlchemy, Argon2, RS256, adaptadores
  interfaces/       # FastAPI: routers, dependencias, JWKS
```

Los puertos (`application/ports.py`) desacoplan el caso de uso de Postgres, Argon2 y PyJWT — fácil de testear con dobles.

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/auth/register` | Crea un usuario (409 si el email ya existe). |
| POST | `/auth/login` | Login JSON → par de tokens. |
| POST | `/auth/token` | OAuth2 password grant (form-urlencoded). |
| POST | `/auth/refresh` | Intercambia refresh por un nuevo par. |
| GET | `/auth/me` | Devuelve claims del access token. |
| GET | `/.well-known/jwks.json` | Clave pública en formato JWK. |
| GET | `/health/live` \| `/health/ready` | Liveness / readiness. |

## Seguridad

- **Argon2id** para contraseñas (OWASP recomendado).
- **RS256** para JWT: sólo auth-service firma; el resto valida con JWKS.
- Claims requeridos: `iss`, `aud`, `exp`, `iat`, `sub`, `typ` (`access`/`refresh`), `jti`.
- Consultas parametrizadas vía SQLAlchemy (sin concatenación de SQL).
- Correlación de requests con `X-Request-ID` propagado entre servicios.
- Contenedor no-root (UID 10001).

## Variables de entorno

| Variable | Por defecto | Descripción |
|---|---|---|
| `DATABASE_URL` | — | Si se define, sobrescribe el DSN calculado. |
| `POSTGRES_HOST` / `_PORT` / `_DB` / `_USER` / `_PASSWORD` | `postgres`/`5432`/`hotelstaff`/`admin`/`admin123` | Conexión. |
| `JWT_PRIVATE_KEY_PATH` | `/run/secrets/jwt_private.pem` | En dev, si no existe, se genera una clave efímera en memoria. |
| `JWT_ISSUER` | `hotelstaff-auth` | Claim `iss`. |
| `JWT_AUDIENCE` | `hotelstaff-api` | Claim `aud`. |
| `JWT_ACCESS_TTL_SECONDS` | `900` (15 min) | TTL del access token. |
| `JWT_REFRESH_TTL_SECONDS` | `604800` (7 días) | TTL del refresh token. |
| `LOG_LEVEL` / `LOG_FORMAT` | `INFO` / `json` | Observabilidad. |

## Comandos

```bash
# Tests con cobertura
pytest --cov=app

# Lint + format
ruff check . --fix
ruff format .

# Migración (requiere Postgres)
alembic upgrade head

# Desarrollo local
uvicorn app.main:app --reload --port 8001
```
