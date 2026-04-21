"""Base común de configuración para todos los microservicios."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    service_name: str = Field(default="hotelstaff-service")
    service_env: str = Field(default="local")
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    rabbitmq_url: str = Field(default="amqp://guest:guest@rabbitmq:5672/")
    rabbitmq_exchange: str = Field(default="hotelstaff.events")

    jwt_algorithm: str = Field(default="RS256")
    jwt_public_key_path: str = Field(default="/run/secrets/jwt_public.pem")
    jwt_issuer: str = Field(default="hotelstaff-auth")
