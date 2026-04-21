# bff — Backend-for-Frontend

API Gateway que agrega los microservicios de HotelStaffIA y es el **único punto de entrada** del frontend.

## Responsabilidades
- Validar el JWT emitido por `auth-service` (JWKS cacheado).
- Aplicar **rate limit** por IP y por `user_id` (Redis).
- Reenviar peticiones al microservicio adecuado vía `@fastify/http-proxy`.
- Propagar `X-Request-ID` para trazabilidad end-to-end.
- Centralizar CORS y cabeceras de seguridad.

No contiene lógica de dominio.

## Desarrollo local

```bash
docker compose up -d redis auth-service user-service role-service audit-service ia-agent
cd bff
npm install
npm run dev
```

## Tests

```bash
npm test
```

## Endpoints

- `GET /health/live`, `GET /health/ready`
- `POST /auth/*` → `auth-service`
- `GET|POST|PATCH|DELETE /users/*` → `user-service`
- `GET|POST|DELETE /roles/*` → `role-service`
- `GET /audit/*` → `audit-service`
- `POST /agent/*` → `ia-agent`
