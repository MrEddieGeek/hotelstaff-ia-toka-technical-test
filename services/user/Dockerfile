# syntax=docker/dockerfile:1.7
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Librería compartida (cachea bien si no cambia)
COPY libs/hotelstaff_shared /opt/hotelstaff_shared
RUN pip install /opt/hotelstaff_shared

# Dependencias del servicio (cachea bien si pyproject no cambia)
COPY services/user/pyproject.toml /app/pyproject.toml
COPY services/user/app /app/app
COPY services/user/tests /app/tests
RUN pip install /app

RUN adduser --disabled-password --gecos "" --uid 10001 appuser && chown -R appuser /app
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=5 \
    CMD curl -fsS http://localhost:8000/health/live || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
