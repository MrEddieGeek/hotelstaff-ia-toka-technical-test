# frontend — HotelStaffIA

Interfaz de gestión construida con Vite + React 18 + TypeScript, Tailwind CSS, Zustand, TanStack Query, React Hook Form + Zod y React Router v6. Todo el copy está en español.

## Desarrollo local

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

Asegúrate de que el BFF esté corriendo en `http://localhost:8080` (configurable con `VITE_BFF_URL`).

## Tests y build

```bash
npm test           # vitest
npm run build      # tsc -b && vite build → dist/
```

## Pantallas

| Ruta | Propósito |
|---|---|
| `/login` | Autenticación contra `auth-service` vía BFF. |
| `/staff` | CRUD de staff (lista + alta + baja). |
| `/roles` | Creación y listado de roles con permisos. |
| `/audit` | Consulta de eventos con filtro por tipo. |
| `/agent` | Preguntas en lenguaje natural al agente IA con visualización de fuentes RAG y latencia. |

## Arquitectura

| Concern | Librería |
|---|---|
| State global | Zustand (con persistencia del token) |
| Server state | TanStack Query |
| Routing | React Router v6 |
| Formularios | React Hook Form + Zod |
| UI | Tailwind + primitivas locales (estilo shadcn) |
| HTTP | Axios centralizado (`src/lib/api.ts`) con inyección automática del `Authorization: Bearer` y logout en 401 |
| Tests | Vitest + React Testing Library |

El cliente HTTP siempre habla con el **BFF** (`/api/*`), nunca con microservicios directamente.

## Variables de entorno

| Variable | Default | Uso |
|---|---|---|
| `VITE_BFF_URL` | `http://localhost:8080` | Base URL del BFF. |

## Dockerización

`Dockerfile` multi-stage construye con Node y sirve `dist/` con nginx (`nginx.conf`), expuesto en el puerto 80 del servicio `frontend` de `docker-compose.yml`.
