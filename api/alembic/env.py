import os
from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context

# .env ada di root repo: api/alembic/env.py -> parents[2]
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

DB_URL = os.environ.get("DATABASE_URL_LOCAL") or os.environ.get("DATABASE_URL")
if not DB_URL:
    raise RuntimeError("Set DATABASE_URL_LOCAL atau DATABASE_URL di .env")
config.set_main_option("sqlalchemy.url", DB_URL.replace("%", "%%"))

target_metadata = None


def run_migrations_offline() -> None:
    context.configure(url=DB_URL, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
