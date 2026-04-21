from __future__ import annotations

from hotelstaff_shared.config import BaseServiceSettings
from pydantic import Field
from pydantic_settings import SettingsConfigDict


class Settings(BaseServiceSettings):
    model_config = SettingsConfigDict(env_prefix="", extra="ignore", case_sensitive=False)

    service_name: str = "user-service"

    postgres_host: str = Field(default="postgres")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="hotelstaff")
    postgres_user: str = Field(default="admin")
    postgres_password: str = Field(default="admin123")

    database_url: str | None = Field(default=None)

    rabbitmq_url: str = Field(default="amqp://guest:guest@rabbitmq:5672/")
    events_exchange: str = Field(default="hotelstaff.events")
    events_enabled: bool = Field(default=True)

    jwt_public_key_path: str | None = Field(default=None)
    jwt_issuer: str = Field(default="hotelstaff-auth")
    jwt_audience: str = Field(default="hotelstaff-api")
    auth_required: bool = Field(default=False)

    demo_seed: bool = Field(default=False)

    @property
    def postgres_dsn(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
