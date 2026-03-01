import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
# Импортируем все модели для их регистрации
# Импортируем наши модели
from shared_models.models import Base  # Используем Base из models.py
from shared_models.models import (Category, Embedding, Message,
                                  MessageEmbedding, Subcategory, Subject, Task,
                                  Topic, User, UserFeedback,
                                  UserKnowledgeRecord, UserMessageExample,
                                  UserProfile, UserStatus)
from shared_models.quiz_model import *
from shared_models.documents_models import *
from shared_models.mentor_models import *

# Добавляем путь к нашему проекту в sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Получаем URL из конфигурации Alembic, а не из database.py
    url = config.get_main_option("sqlalchemy.url")
    
    # Если URL не найден в конфигурации, используем из database.py как fallback
    if not url:
        from shared_models.database import DATABASE_URL
        url = DATABASE_URL

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Получаем URL из конфигурации Alembic, а не из database.py
    url = config.get_main_option("sqlalchemy.url")
    
    # Если URL не найден в конфигурации, используем из database.py как fallback
    if not url:
        from shared_models.database import DATABASE_URL
        url = DATABASE_URL

    # Получаем секцию конфигурации
    configuration = config.get_section(config.config_ini_section)
    if configuration is None:
        configuration = {}

    # Создаем движок с URL из конфигурации
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=url,  # Явно передаем URL
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
