# HotelStaffIA — Prueba Técnica Senior Full-Stack Engineer (IA) | Toka

**Autor:** Edgar Guzmán Enríquez (`@MrEddieGeek`)
**Fecha:** Abril 2026

Sistema de gestión de staff de hotel con microservicios, BFF, frontend React y agente IA con RAG. Cubre los 5 ejercicios de la prueba técnica de Toka.

---

## 🗺️ Arquitectura

Diagrama completo, justificación técnica (DDD + Clean Architecture), flujo de datos end-to-end, estrategia de seguridad y resiliencia: [`docs/arquitectura.md`](./docs/arquitectura.md).

En una línea: **React** → **BFF (Fastify)** → **microservicios FastAPI** (auth, user, role, audit, ia-agent) sobre **Postgres / MongoDB / Redis / RabbitMQ / Qdrant**.

---

## 📁 Estructura del repositorio

```
hotelstaff-ia-toka-technical-test/
├── bff/                         Node.js + Fastify + TS (API Gateway)
├── frontend/                    Vite + React + TS + shadcn/ui + Zustand
├── services/
│   ├── auth/                    FastAPI + Postgres + JWT/OAuth2
│   ├── user/                    FastAPI + Postgres + RabbitMQ publisher
│   ├── role/                    FastAPI + Postgres (RBAC)
│   ├── audit/                   FastAPI + MongoDB + RabbitMQ consumer
│   └── ia-agent/                FastAPI + Qdrant + OpenAI/Gemini (RAG)
├── libs/
│   └── hotelstaff_shared/       Logging, config base, eventos, EventBus, JWT verifier
├── infra/
│   └── postgres/init/           Schemas y roles por servicio
├── docs/                        Documentación por ejercicio
├── docker-compose.yml           Orquestación completa
├── Makefile                     Atajos de DX
└── .env.example                 Plantilla de variables de entorno
```

Cada microservicio sigue Clean Architecture: `app/{domain,application,infrastructure,interfaces}`.

---

## 🚀 Cómo levantar el entorno

Requisitos: Docker y Docker Compose v2, `make`, `openssl` (para generar llaves JWT).

```bash
cp .env.example .env           # ajusta OPENAI_API_KEY y contraseñas
make keys                      # genera par RSA para firmar JWTs (./secrets/)
make up                        # levanta infra + servicios + BFF + frontend
```

URLs:

| Servicio | URL |
|---|---|
| Frontend | http://localhost:3000 |
| BFF | http://localhost:8080 |
| auth-service | http://localhost:8001 |
| user-service | http://localhost:8002 |
| role-service | http://localhost:8003 |
| audit-service | http://localhost:8004 |
| ia-agent | http://localhost:8005 |
| RabbitMQ UI | http://localhost:15672 (guest/guest) |
| Qdrant UI | http://localhost:6333/dashboard |

Otros comandos útiles:

```bash
make up-infra        # sólo postgres/mongo/redis/rabbit/qdrant
make logs s=user-service
make test            # tests de todos los servicios
make test-cov        # tests + coverage report
make clean           # down + elimina volúmenes
```

---

## ✅ Cobertura de los 5 ejercicios

| Ejercicio | Entregable | Estado |
|---|---|---|
| **E1** — Diseño y arquitectura | [`docs/arquitectura.md`](./docs/arquitectura.md) | ✅ |
| **E2** — Microservicios | `services/auth`, `services/user`, `services/role`, `services/audit` | 🏗️ scaffold |
| **E3** — Frontend | `frontend/` | 🏗️ scaffold |
| **E4** — Diagnóstico | `docs/ejercicio4-diagnostico.md` | ⏳ |
| **E5** — Agente IA | `services/ia-agent/` | 🏗️ scaffold |

El criterio para dar un ejercicio por terminado: **demostrable de forma aislada** (endpoint, comando o pantalla) con evidencia ejecutable.

---

## 📬 Contacto

Edgar Guzmán Enríquez — [github.com/MrEddieGeek](https://github.com/MrEddieGeek)
