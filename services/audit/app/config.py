from __future__ import annotations

from hotelstaff_shared.config import BaseServiceSettings
from pydantic import Field
from pydantic_settings import SettingsConfigDict


class Settings(BaseServiceSettings):
    model_config = SettingsConfigDict(env_prefix="", extra="ignore", case_sensitive=False)

    service_name: str = "audit-service"

    mongo_uri: str = Field(default="mongodb://mongodb:27017")
    mongo_db: str = Field(default="hotelstaff_audit")
    use_mongomock: bool = Field(default=False)

    rabbitmq_url: str = Field(default="amqp://guest:guest@rabbitmq:5672/")
    events_exchange: str = Field(default="hotelstaff.events")
    events_queue: str = Field(default="audit.events")
    consumer_enabled: bool = Field(default=True)


settings = Settings()
