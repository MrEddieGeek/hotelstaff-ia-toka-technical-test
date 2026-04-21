from __future__ import annotations

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from hotelstaff_shared.config import BaseServiceSettings


class Settings(BaseServiceSettings):
    model_config = SettingsConfigDict(env_prefix="", extra="ignore", case_sensitive=False)

    service_name: str = "audit-service"

    mongo_uri: str = Field(default="mongodb://mongodb:27017")
    mongo_db: str = Field(default="hotelstaff_audit")


settings = Settings()
