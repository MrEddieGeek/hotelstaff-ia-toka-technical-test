from __future__ import annotations

from sqlalchemy import engine_from_config, pool

from alembic import context
from app.config import settings
from app.infrastructure.db.models import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.postgres_dsn.replace("+asyncpg", ""))
target_metadata = Base.metadata

connectable = engine_from_config(
    config.get_section(config.config_ini_section, {}),
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
)
with connectable.connect() as connection:
    context.configure(connection=connection, target_metadata=target_metadata, include_schemas=True)
    with context.begin_transaction():
        context.run_migrations()
