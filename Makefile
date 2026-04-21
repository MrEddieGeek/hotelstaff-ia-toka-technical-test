.PHONY: help up down build rebuild logs ps clean test test-cov lint format keys

# Objetivo por defecto: mostrar ayuda
help:
	@echo "HotelStaffIA — comandos disponibles:"
	@echo ""
	@echo "  make up           Levanta todo el stack (infra + servicios + frontend)"
	@echo "  make up-infra     Levanta sólo infraestructura (postgres, mongo, redis, rabbitmq, qdrant)"
	@echo "  make down         Detiene y elimina contenedores"
	@echo "  make build        Construye todas las imágenes"
	@echo "  make rebuild      Reconstruye desde cero (sin caché)"
	@echo "  make logs s=X     Muestra logs de un servicio (ej: make logs s=auth-service)"
	@echo "  make ps           Lista contenedores"
	@echo "  make clean        Elimina contenedores, volúmenes y redes"
	@echo ""
	@echo "  make test         Corre tests de todos los servicios"
	@echo "  make test-cov     Tests + reporte de cobertura"
	@echo "  make lint         Linting (ruff + eslint)"
	@echo "  make format       Formateo (ruff format + prettier)"
	@echo ""
	@echo "  make keys         Genera par de llaves RSA para firmar JWTs (./secrets/)"

up:
	docker compose up --build -d
	@echo "Stack levantado. Frontend: http://localhost:$${FRONTEND_PORT:-3000}"

up-infra:
	docker compose up -d postgres mongodb redis rabbitmq qdrant

down:
	docker compose down

build:
	docker compose build

rebuild:
	docker compose build --no-cache

logs:
	@test -n "$(s)" || (echo "Uso: make logs s=<servicio>"; exit 1)
	docker compose logs -f $(s)

ps:
	docker compose ps

clean:
	docker compose down -v --remove-orphans

test:
	@for svc in auth user role audit ia-agent; do \
		echo "\n==> tests: services/$$svc"; \
		(cd services/$$svc && python -m pytest -q) || exit 1; \
	done
	@echo "\n==> tests: frontend"
	@cd frontend && npm test -- --run
	@echo "\n==> tests: bff"
	@cd bff && npm test

test-cov:
	@for svc in auth user role audit ia-agent; do \
		echo "\n==> coverage: services/$$svc"; \
		(cd services/$$svc && python -m pytest --cov=app --cov-report=term-missing --cov-report=xml) || exit 1; \
	done

lint:
	@for svc in auth user role audit ia-agent; do \
		(cd services/$$svc && ruff check . && ruff format --check .) || exit 1; \
	done
	@cd bff && npm run lint
	@cd frontend && npm run lint

format:
	@for svc in auth user role audit ia-agent; do \
		(cd services/$$svc && ruff format . && ruff check --fix .); \
	done
	@cd bff && npm run format
	@cd frontend && npm run format

keys:
	@mkdir -p secrets
	@test -f secrets/jwt_private.pem || openssl genrsa -out secrets/jwt_private.pem 2048
	@test -f secrets/jwt_public.pem || openssl rsa -in secrets/jwt_private.pem -pubout -out secrets/jwt_public.pem
	@echo "Llaves generadas en ./secrets/ (ignoradas por git)"
