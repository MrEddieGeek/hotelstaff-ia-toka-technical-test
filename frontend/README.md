# frontend — HotelStaffIA

Interfaz de gestión construida con Vite + React + TypeScript, shadcn/ui, Tailwind CSS, Zustand y TanStack Query.

## Desarrollo local

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

Asegúrate de que el BFF esté corriendo:

```bash
docker compose up -d bff
# o, desde la raíz:
make up
```

## Tests

```bash
npm test
```

## Build

```bash
npm run build      # genera dist/ (servido por nginx en Docker)
```

## Stack

| Concern | Librería |
|---|---|
| State global | Zustand |
| Server state | TanStack Query |
| Routing | React Router v6 |
| Formularios | React Hook Form + Zod |
| UI | shadcn/ui + Tailwind |
| HTTP | Axios (cliente centralizado en `src/api/`) |
| Tests | Vitest + React Testing Library |

## Estructura prevista (se llena en E3)

```
src/
├── App.tsx
├── main.tsx
├── api/              # Cliente Axios + endpoints tipados
├── components/ui/    # Componentes de shadcn
├── features/         # Login, Users, Roles, Audit, AgentePanel
├── hooks/
├── lib/
├── store/            # Stores Zustand
└── routes/           # Configuración de rutas
```
