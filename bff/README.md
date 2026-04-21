# bff — Backend-for-Frontend

API Gateway en Fastify + TypeScript. Es el **único punto de entrada** del frontend hacia los microservicios de HotelStaffIA.

## Responsabilidades

- Verifica el JWT RS256 emitido por `auth-service` descargando el JWKS remoto (`/.well-known/jwks.json`) con caché en memoria.
- Aplica **rate limit** por IP (`@fastify/rate-limit`).
- Reenvía peticiones al microservicio destino preservando `Authorization`, `Content-Type`, query string y cuerpo (`fetch` nativo).
- Propaga `X-Request-ID` extremo a extremo para trazabilidad.
- Centraliza CORS. No contiene lógica de dominio.

## Endpoints expuestos

Todas las rutas cuelgan de `/api/*` salvo health:

| Método | Ruta | Destino | Auth |
|---|---|---|---|
| POST | `/api/auth/register` `/login` `/token` `/refresh` | auth-service | público |
| GET | `/api/auth/me` | auth-service | Bearer |
| CRUD | `/api/users[/:id]` | user-service | Bearer |
| POST/GET | `/api/roles` | role-service | Bearer |
| POST/DELETE | `/api/assignments` | role-service | Bearer |
| GET | `/api/users/:userId/roles` | role-service | Bearer |
| GET | `/api/audit/logs[/:eventId]` | audit-service | Bearer |
| POST | `/api/agent/ask` `/index` `/index/bulk` | ia-agent | Bearer |
| GET | `/health/live` `/health/ready` | — | público |

## Variables de entorno

| Variable | Default |
|---|---|
| `BFF_PORT` | `8080` |
| `BFF_CORS_ORIGIN` | `http://localhost:3000` |
| `AUTH_SERVICE_URL` · `USER_SERVICE_URL` · `ROLE_SERVICE_URL` · `AUDIT_SERVICE_URL` · `IA_AGENT_URL` | DNS interno de compose |
| `JWT_ISSUER` | `hotelstaff-auth` |
| `JWT_ALGORITHM` | `RS256` |
| `RATE_LIMIT_MAX` · `RATE_LIMIT_WINDOW` | `200` · `1 minute` |

## Desarrollo

```bash
docker compose up -d auth-service user-service role-service audit-service ia-agent
cd bff
npm install
npm run dev
```

## Tests y build

```bash
npm test      # vitest (health + auth/forwarding)
npm run build # tsc
```

Los tests mockean `fetch` global para verificar reenvío sin tocar microservicios reales.
