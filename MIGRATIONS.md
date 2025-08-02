# Работа с миграциями Alembic

## Настройка

1. **Установка зависимостей:**
```bash
poetry install
```

2. **Настройка переменных окружения:**
Скопируйте `.env.example` в `.env` и настройте подключение к базе данных:
```bash
cp .env.example .env
```

3. **Настройка базы данных PostgreSQL:**
Убедитесь, что PostgreSQL запущен и доступен по адресу из `.env` файла.

## Основные команды Alembic

### Создание новой миграции
```bash
# Автогенерация миграции на основе изменений в моделях
poetry run alembic revision --autogenerate -m "Описание изменений"

# Создание пустой миграции
poetry run alembic revision -m "Описание изменений"
```

### Применение миграций
```bash
# Применить все неприменённые миграции
poetry run alembic upgrade head

# Применить до конкретной миграции
poetry run alembic upgrade <revision_id>

# Применить следующую миграцию
poetry run alembic upgrade +1
```

### Откат миграций
```bash
# Откатить одну миграцию
poetry run alembic downgrade -1

# Откатить до конкретной миграции
poetry run alembic downgrade <revision_id>

# Откатить все миграции
poetry run alembic downgrade base
```

### Информация о миграциях
```bash
# Показать текущую версию
poetry run alembic current

# Показать историю миграций
poetry run alembic history

# Показать неприменённые миграции
poetry run alembic heads
```

## Структура проекта

```
shared_models/
├── __init__.py          # Экспорты моделей и схем
├── models.py            # SQLAlchemy модели
├── schemas.py           # Pydantic схемы и Enums
└── database.py          # Настройка подключения к БД

alembic/
├── env.py              # Конфигурация Alembic
├── versions/           # Файлы миграций
└── script.py.mako      # Шаблон для новых миграций

alembic.ini             # Основная конфигурация Alembic
```

## Модели

Проект содержит следующие модели:

- **User** - Пользователи системы
- **Topic** - Темы форума
- **Message** - Сообщения в темах
- **Embedding** - Векторные представления
- **MessageEmbedding** - Эмбеддинги сообщений
- **UserKnowledgeRecord** - Знания пользователей
- **UserMessageExample** - Примеры сообщений пользователей

## Просмотр состояния базы данных

### Проверка Docker контейнера
```bash
# Проверить статус контейнеров
docker-compose ps

# Просмотр логов PostgreSQL
docker-compose logs postgres

# Перезапуск контейнера
docker-compose down
docker-compose up --build -d
```

### Проверка структуры базы данных
```bash
# Список всех таблиц
docker exec forum_postgres psql -U docker -d postgres -c "\dt"

# Подробная информация о таблице
docker exec forum_postgres psql -U docker -d postgres -c "\d+ users"
docker exec forum_postgres psql -U docker -d postgres -c "\d+ message_embeddings"

# Проверка внешних ключей и связей
docker exec forum_postgres psql -U docker -d postgres -c "\d message_embeddings"

# Список установленных расширений
docker exec forum_postgres psql -U docker -d postgres -c "\dx"

# Проверка pgvector
docker exec forum_postgres psql -U docker -d postgres -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### Просмотр данных
```bash
# Количество записей в таблицах
docker exec forum_postgres psql -U docker -d postgres -c "
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_rows
FROM pg_stat_user_tables 
ORDER BY tablename;"

# Размеры таблиц
docker exec forum_postgres psql -U docker -d postgres -c "
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

### Полезные SQL-запросы для диагностики
```bash
# Проверка активных соединений
docker exec forum_postgres psql -U docker -d postgres -c "
SELECT pid, usename, application_name, client_addr, state, query 
FROM pg_stat_activity 
WHERE state = 'active';"

# Проверка блокировок
docker exec forum_postgres psql -U docker -d postgres -c "
SELECT blocked_locks.pid AS blocked_pid,
       blocked_activity.usename AS blocked_user,
       blocking_locks.pid AS blocking_pid,
       blocking_activity.usename AS blocking_user,
       blocked_activity.query AS blocked_statement,
       blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
WHERE NOT blocked_locks.granted;"

# Проверка версии PostgreSQL и pgvector
docker exec forum_postgres psql -U docker -d postgres -c "
SELECT version();
SELECT * FROM pg_available_extensions WHERE name = 'vector';"

# Проверка структуры индексов
docker exec forum_postgres psql -U docker -d postgres -c "
SELECT 
    t.relname as table_name,
    i.relname as index_name,
    array_to_string(array_agg(a.attname), ', ') as column_names
FROM pg_class t,
     pg_class i,
     pg_index ix,
     pg_attribute a
WHERE t.oid = ix.indrelid
  AND i.oid = ix.indexrelid
  AND a.attrelid = t.oid
  AND a.attnum = ANY(ix.indkey)
  AND t.relkind = 'r'
  AND t.relname IN ('users', 'topics', 'messages', 'message_embeddings', 'user_message_examples')
GROUP BY t.relname, i.relname
ORDER BY t.relname, i.relname;"
```

## Тестирование подключения и связей

### Базовый тест подключения
```bash
poetry run python test_db.py
```

### Тест каскадных удалений и связей
```bash
poetry run python test_relationships.py
```

## Переменные окружения

| Переменная | Описание | Пример |
|------------|----------|---------|
| `DATABASE_URL` | URL подключения к БД | `postgresql+psycopg2://user:pass@localhost:5432/db` |
| `DB_POOL_SIZE` | Размер пула соединений | `5` |
| `DB_MAX_OVERFLOW` | Максимальный overflow пула | `10` |
| `DB_POOL_TIMEOUT` | Таймаут пула (сек) | `30` |
| `DB_POOL_RECYCLE` | Время жизни соединения (сек) | `3600` |
| `LOG_LEVEL` | Уровень логирования | `DEBUG` / `INFO` |

## Troubleshooting

### Ошибка подключения к PostgreSQL
1. Убедитесь, что PostgreSQL запущен
2. Проверьте правильность данных в `.env`
3. Убедитесь, что база данных существует

### Ошибка импорта pgvector
1. Установите расширение в PostgreSQL: `CREATE EXTENSION vector;`
2. Убедитесь, что pgvector установлен: `poetry add pgvector`

### Ошибки миграций
1. Проверьте синтаксис в файлах моделей
2. Убедитесь, что все модели импортированы в `alembic/env.py`
3. Проверьте, что нет конфликтующих изменений в БД

### Сброс и пересоздание миграций
```bash
# Удаление всех миграций
rm -rf alembic/versions/*.py
rm -rf alembic/versions/__pycache__

# Полная очистка схемы базы данных
docker exec forum_postgres psql -U docker -d postgres -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; CREATE EXTENSION IF NOT EXISTS vector;"

# Создание новой начальной миграции
poetry run alembic revision --autogenerate -m "Initial migration: create all tables with proper relationships"

# Применение миграции
poetry run alembic upgrade head

# Проверка результата
poetry run alembic current
poetry run alembic history
```

### Быстрые команды для разработки
```bash
# Активация виртуального окружения и создание миграции
source .venv/bin/activate && alembic revision --autogenerate -m "Initial migration: create all tables"

# Полный сброс с пересозданием
docker exec forum_postgres psql -U docker -d postgres -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; CREATE EXTENSION IF NOT EXISTS vector;"
```

## Полезные алиасы для разработки

Добавьте эти алиасы в ваш `~/.zshrc` или `~/.bashrc` для быстрого доступа:

```bash
# Алиасы для работы с shared-models
alias sm-db-reset='docker exec forum_postgres psql -U docker -d postgres -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; CREATE EXTENSION IF NOT EXISTS vector;"'
alias sm-migration-create='poetry run alembic revision --autogenerate -m'
alias sm-migration-upgrade='poetry run alembic upgrade head'
alias sm-migration-current='poetry run alembic current'
alias sm-migration-history='poetry run alembic history'
alias sm-db-tables='docker exec forum_postgres psql -U docker -d postgres -c "\dt"'
alias sm-db-extensions='docker exec forum_postgres psql -U docker -d postgres -c "\dx"'
alias sm-test-relations='poetry run python test_relationships.py'
alias sm-docker-up='docker-compose up -d'
alias sm-docker-down='docker-compose down'
alias sm-docker-logs='docker-compose logs postgres'

# Пример использования:
# sm-db-reset && sm-migration-create "Add new field" && sm-migration-upgrade
```

## Автоматическое применение миграций при старте

### Вариант 1: Docker Compose с init-контейнером
Создайте отдельный контейнер для миграций в `docker-compose.yml`:

```yaml
services:
  postgres:
    # ... существующая конфигурация PostgreSQL
    
  migration:
    build: .
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql+psycopg2://docker:docker@postgres:5432/postgres
    command: |
      sh -c "
        echo 'Waiting for database to be ready...'
        poetry install
        poetry run alembic upgrade head
        echo 'Migrations applied successfully!'
      "
    volumes:
      - .:/app
    working_dir: /app
    networks:
      - ai_network

  # Ваше основное приложение
  app:
    build: .
    depends_on:
      - migration
    # ... остальная конфигурация
```

### Вариант 2: Скрипт инициализации в основном контейнере
Создайте скрипт `scripts/entrypoint.sh`:

```bash
#!/bin/bash
set -e

# Функция для проверки доступности базы данных
wait_for_db() {
    echo "Waiting for database..."
    while ! python -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(
        host='postgres',
        database='postgres', 
        user='docker',
        password='docker'
    )
    conn.close()
    print('Database is ready!')
except:
    exit(1)
    "; do
        sleep 1
    done
}

# Применение миграций
apply_migrations() {
    echo "Applying database migrations..."
    poetry run alembic upgrade head
    if [ $? -eq 0 ]; then
        echo "Migrations applied successfully!"
    else
        echo "Migration failed!"
        exit 1
    fi
}

# Проверка статуса миграций
check_migrations() {
    echo "Checking migration status..."
    current=$(poetry run alembic current 2>/dev/null | grep -o '[a-f0-9]\{12\}' | head -1)
    head=$(poetry run alembic heads 2>/dev/null | grep -o '[a-f0-9]\{12\}' | head -1)
    
    if [ "$current" = "$head" ]; then
        echo "Database is up to date (revision: $current)"
    else
        echo "Database needs migration. Current: $current, Head: $head"
        apply_migrations
    fi
}

# Основная логика
main() {
    wait_for_db
    check_migrations
    
    # Запуск основного приложения
    exec "$@"
}

main "$@"
```

Сделайте скрипт исполняемым и используйте его как entrypoint:
```bash
chmod +x scripts/entrypoint.sh
```

### Вариант 3: Docker Healthcheck с миграциями
Добавьте в `docker-compose.yml`:

```yaml
services:
  postgres:
    # ... существующая конфигурация
    
  app:
    build: .
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql+psycopg2://docker:docker@postgres:5432/postgres
    command: |
      sh -c "
        poetry run alembic current || poetry run alembic upgrade head
        poetry run alembic upgrade head
        # Запуск вашего приложения
        python main.py
      "
    healthcheck:
      test: ["CMD", "poetry", "run", "alembic", "current"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Вариант 4: Makefile для автоматизации
Создайте `Makefile`:

```makefile
.PHONY: up migrate check-migrations

# Запуск с автоматическими миграциями
up:
	docker-compose up -d postgres
	@echo "Waiting for PostgreSQL to be ready..."
	@until docker exec forum_postgres pg_isready -U docker -d postgres; do sleep 1; done
	poetry run alembic upgrade head
	docker-compose up -d

# Только миграции
migrate:
	poetry run alembic upgrade head

# Проверка статуса миграций
check-migrations:
	@echo "Current migration:"
	poetry run alembic current
	@echo "Available migrations:"
	poetry run alembic heads
	@echo "History:"
	poetry run alembic history --verbose

# Полный сброс и настройка
reset-and-migrate:
	docker-compose down
	docker volume rm shared-models_postgres_data || true
	docker-compose up -d postgres
	@until docker exec forum_postgres pg_isready -U docker -d postgres; do sleep 1; done
	poetry run alembic upgrade head
```

Использование:
```bash
make up              # Запуск с миграциями
make migrate         # Только применить миграции
make check-migrations # Проверить статус
make reset-and-migrate # Полный сброс
```

### Вариант 5: Готовые скрипты (Рекомендуемый)
В проекте уже созданы готовые инструменты:

```bash
# Makefile команды для ежедневной работы
make help                    # Показать все доступные команды
make up                      # Запуск PostgreSQL + автоматические миграции
make check-migrations        # Проверить статус миграций
make create-migration MESSAGE="описание"  # Создать новую миграцию
make reset-and-migrate       # Полный сброс с миграциями
make test-relations          # Тест каскадного удаления

# Быстрая проверка статуса
./scripts/check-migration-status.sh

# Docker Compose с миграциями
docker-compose -f docker-compose.migration.yml up

# Entrypoint скрипт для production
./scripts/entrypoint.sh python main.py
```

## Рекомендуемый workflow для разработки

### Ежедневная работа:
```bash
# 1. Запуск с автоматическими миграциями
make up

# 2. Работа с кодом...

# 3. Создание новой миграции
make create-migration MESSAGE="Add new field to users"

# 4. Проверка статуса
make check-migrations

# 5. Тестирование связей
make test-relations
```

### При проблемах:
```bash
# Полный сброс
make reset-and-migrate

# Или вручную
make down
docker volume rm shared-models_postgres_data
make up
```

### В production:
```bash
# Использование entrypoint скрипта
docker run -e DATABASE_URL=... myapp ./scripts/entrypoint.sh python main.py

# Или отдельный init-контейнер в docker-compose
docker-compose -f docker-compose.migration.yml up migration
```

## Сборка Docker образа без docker-compose

### Основные команды Docker

```bash
# Сборка образа PostgreSQL с shared-models
docker build -t shared-models:postgres .

# Запуск PostgreSQL с автоматическими миграциями
docker run -d \
  --name shared-models-postgres \
  -p 5432:5432 \
  -e POSTGRES_DB=postgres \
  -e POSTGRES_USER=docker \
  -e POSTGRES_PASSWORD=docker \
  -v shared_models_data:/var/lib/postgresql/data \
  shared-models:postgres

# Проверка логов (миграции применяются при первом запуске)
docker logs -f shared-models-postgres

# Подключение к PostgreSQL
docker exec -it shared-models-postgres psql -U docker -d postgres

# Проверка статуса миграций
docker exec -it shared-models-postgres /app/scripts/check-migration-status.sh
```

### Makefile команды для Docker

```bash
# Основные команды
make docker-build              # Собрать образ PostgreSQL с shared-models
make docker-run-postgres       # Запустить PostgreSQL с автоматическими миграциями
make docker-logs              # Показать логи контейнера
make docker-psql              # Подключиться к PostgreSQL
make docker-shell             # Подключиться к bash в контейнере
make docker-stop              # Остановить контейнер
make docker-test              # Проверить статус миграций

# Примеры использования
make docker-build && make docker-run-postgres
make docker-logs               # В другом терминале
```

### Работа с данными

```bash
# Создание volume для данных
docker volume create shared_models_data

# Запуск с постоянным хранилищем
docker run -d \
  --name shared-models-postgres \
  -p 5432:5432 \
  -v shared_models_data:/var/lib/postgresql/data \
  shared-models:postgres

# Backup данных
docker exec shared-models-postgres pg_dump -U docker postgres > backup.sql

# Восстановление данных
cat backup.sql | docker exec -i shared-models-postgres psql -U docker postgres

# Очистка данных
docker volume rm shared_models_data
```