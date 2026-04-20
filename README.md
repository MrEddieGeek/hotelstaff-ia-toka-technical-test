# HotelStaffIA — Prueba Técnica Senior Full-Stack Engineer (IA) | Toka

**Autor:** Edgar Guzmán Enríquez (`@MrEddieGeek`)
**Fecha:** Abril 2026
**Estado:** En desarrollo activo

Este repositorio es la entrega de la prueba técnica de Toka para el puesto de Senior Full-Stack Engineer con foco en IA. Cubre los 5 ejercicios solicitados y deja la base de un demo reutilizable como CRM de staff de hotel con agente IA integrado.

---

## 📚 Documentos clave

| Archivo | Propósito |
|---|---|
| [`repo-structure.md`](./repo-structure.md) | Estructura prevista del repositorio. |
| [`docker-compose.yml`](./docker-compose.yml) | Orquestación local de todos los servicios e infraestructura. |
| `docs/` | Documentación de arquitectura y por ejercicio (conforme se entrega). |

---

## 🏗️ Arquitectura en una línea

**Frontend (React + TS + shadcn/ui + Zustand)** → **BFF** → **Microservicios FastAPI** (auth, user, role, audit, ia-agent) sobre **Postgres / MongoDB / Redis / RabbitMQ / Qdrant**.

El detalle, el diagrama Mermaid y la justificación de cada decisión están documentados en `docs/` (Ejercicio 1).

---

## 🚀 Cómo levantar el entorno

Requisitos: Docker y Docker Compose v2.

```bash
# Stack completo (infra + servicios + frontend)
docker compose up --build

# Sólo infraestructura (para desarrollar un servicio localmente)
docker compose up postgres mongodb redis rabbitmq qdrant

# Ver logs de un servicio
docker compose logs -f <servicio>
```

Puertos expuestos en local:

| Servicio | Puerto |
|---|---|
| Frontend | 3000 |
| Postgres | 5432 |
| MongoDB | 27017 |
| Redis | 6379 |
| RabbitMQ (AMQP) | 5672 |
| RabbitMQ (management UI) | 15672 |
| Qdrant | 6333 |

Cada microservicio dispondrá de su propio `README.md` con instrucciones de desarrollo aislado, tests y linting conforme se vaya implementando.

---

## ✅ Cobertura de los 5 ejercicios

El avance por ejercicio se documenta en `docs/`. El criterio para dar un ejercicio por terminado es que sea **demostrable de forma aislada** (endpoint, comando o pantalla) con evidencia ejecutable, no sólo código.

---

## 📬 Contacto

Edgar Guzmán Enríquez — [github.com/MrEddieGeek](https://github.com/MrEddieGeek)
