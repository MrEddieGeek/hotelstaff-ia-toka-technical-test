from __future__ import annotations

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from hotelstaff_shared.config import BaseServiceSettings


class Settings(BaseServiceSettings):
    model_config = SettingsConfigDict(env_prefix="", extra="ignore", case_sensitive=False)

    service_name: str = "auth-service"

    postgres_host: str = Field(default="postgres")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="hotelstaff")
    postgres_user: str = Field(default="admin")
    postgres_password: str = Field(default="admin123")

    redis_url: str = Field(default="redis://redis:6379/0")

    jwt_private_key_path: str = Field(default="/run/secrets/jwt_private.pem")
    jwt_access_ttl_seconds: int = Field(default=900)
    jwt_refresh_ttl_seconds: int = Field(default=604800)

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
