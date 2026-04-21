from __future__ import annotations

from hotelstaff_shared.config import BaseServiceSettings
from pydantic import Field
from pydantic_settings import SettingsConfigDict


class Settings(BaseServiceSettings):
    model_config = SettingsConfigDict(env_prefix="", extra="ignore", case_sensitive=False)

    service_name: str = "ia-agent"

    qdrant_url: str = Field(default="http://qdrant:6333")
    qdrant_collection: str = Field(default="hotelstaff_users")
    use_memory_vector_store: bool = Field(default=False)

    llm_provider: str = Field(default="stub")  # openai|gemini|stub
    openai_api_key: str = Field(default="")
    openai_model: str = Field(default="gpt-4o-mini")
    openai_embedding_model: str = Field(default="text-embedding-3-small")
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-1.5-flash")

    rabbitmq_url: str = Field(default="amqp://guest:guest@rabbitmq:5672/")
    events_exchange: str = Field(default="hotelstaff.events")
    events_queue: str = Field(default="ia-agent.events")
    consumer_enabled: bool = Field(default=True)


settings = Settings()
