# Dockerfile на основе pgvector/pgvector:pg15
FROM pgvector/pgvector:pg15

# Метаданные образа
LABEL maintainer="ViachaslauKazakou"
LABEL description="PostgreSQL с pgvector и shared-models миграциями"
LABEL version="0.1.1"

# Установка базовых пакетов
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-full \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry с --break-system-packages для Docker окружения
ENV POETRY_VERSION=2.1.0
RUN pip3 install --break-system-packages poetry==$POETRY_VERSION

# Установка Poetry плагинов
RUN poetry self add poetry-plugin-export

# Настройка Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Создание рабочей директории для приложения
RUN mkdir -p /app
WORKDIR /app

# Копирование файлов проекта
COPY pyproject.toml poetry.lock ./
COPY shared_models/ ./shared_models/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY scripts/ ./scripts/

# Установка Python зависимостей
RUN poetry install --only=main && rm -rf $POETRY_CACHE_DIR

# Делаем скрипты исполняемыми
RUN chmod +x scripts/*.sh

# Копирование кастомного init скрипта
COPY docker/init-pgvector.sql /docker-entrypoint-initdb.d/01-init-pgvector.sql
COPY docker/init-migrations.sh /docker-entrypoint-initdb.d/02-init-migrations.sh

# Делаем migration скрипт исполняемым
RUN chmod +x /docker-entrypoint-initdb.d/02-init-migrations.sh

# Переменные окружения для PostgreSQL
ENV POSTGRES_DB=postgres
ENV POSTGRES_USER=docker
ENV POSTGRES_PASSWORD=docker
ENV POSTGRES_HOST_AUTH_METHOD=trust

# Переменные окружения для миграций
ENV DATABASE_URL=postgresql+psycopg2://docker:docker@localhost:5432/postgres
ENV PYTHONPATH=/app

# Открытие стандартного порта PostgreSQL
EXPOSE 5432

# Использование стандартного entrypoint от PostgreSQL
# который автоматически выполнит скрипты из /docker-entrypoint-initdb.d/
