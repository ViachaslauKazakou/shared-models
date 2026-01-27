# Используем официальный Python 3.12 образ как базовый
FROM python:3.12-bookworm

# Установка PostgreSQL 15 с pgvector
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    gnupg \
    lsb-release \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update \
    && apt-get install -y \
    postgresql-15 \
    postgresql-client-15 \
    postgresql-contrib-15 \
    postgresql-15-pgvector \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя postgres если не существует
RUN groupadd -r postgres --gid=999 || true \
    && useradd -r -g postgres --uid=999 --home-dir=/var/lib/postgresql --shell=/bin/bash postgres || true

# Создание директорий для PostgreSQL
RUN mkdir -p /var/lib/postgresql/data \
    && chown -R postgres:postgres /var/lib/postgresql \
    && chmod 777 /var/lib/postgresql/data

# Настройка переменных окружения для PostgreSQL
ENV PGVERSION=15
ENV PATH=$PATH:/usr/lib/postgresql/$PGVERSION/bin
ENV PGDATA=/var/lib/postgresql/data

# Метаданные образа
LABEL maintainer="ViachaslauKazakou"
LABEL description="PostgreSQL с pgvector и shared-models миграциями"
LABEL version="0.1.1"



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

# Создание директории для init скриптов
RUN mkdir -p /docker-entrypoint-initdb.d

# Копирование entry point скрипта
COPY --from=pgvector/pgvector:pg15 /usr/local/bin/docker-entrypoint.sh /usr/local/bin/

# Делаем entry point исполняемым
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Использование стандартного entrypoint от PostgreSQL
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["postgres"]
