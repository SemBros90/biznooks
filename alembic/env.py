from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# set DB URL from env if present
db_url = os.environ.get('DATABASE_URL')
if db_url:
    config.set_main_option('sqlalchemy.url', db_url)

from sqlmodel import SQLModel
from backend.app import models

# add your model's MetaData object here
target_metadata = SQLModel.metadata

def run_migrations_offline():
    context.configure(url=config.get_main_option('sqlalchemy.url'))
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
