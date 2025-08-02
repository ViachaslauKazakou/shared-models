.PHONY: help up down migrate check-migrations reset-and-migrate test-relations clean logs

# Цвета для вывода
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m # No Color

help: ## Показать справку по командам
	@echo "$(GREEN)Доступные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

up: ## Запуск с автоматическими миграциями
	@echo "$(GREEN)Starting PostgreSQL...$(NC)"
	docker-compose up -d postgres
	@echo "$(YELLOW)Waiting for PostgreSQL to be ready...$(NC)"
	@until docker exec forum_postgres pg_isready -U docker -d postgres >/dev/null 2>&1; do sleep 1; done
	@echo "$(GREEN)Applying migrations...$(NC)"
	poetry run alembic upgrade head
	@echo "$(GREEN)All services are ready!$(NC)"

down: ## Остановка всех контейнеров
	@echo "$(YELLOW)Stopping containers...$(NC)"
	docker-compose down

migrate: ## Только применить миграции
	@echo "$(GREEN)Applying migrations...$(NC)"
	poetry run alembic upgrade head

check-migrations: ## Проверить статус миграций
	@echo "$(GREEN)Current migration:$(NC)"
	@poetry run alembic current || echo "$(RED)No migrations applied$(NC)"
	@echo "\n$(GREEN)Available migrations:$(NC)"
	@poetry run alembic heads || echo "$(RED)No migrations found$(NC)"
	@echo "\n$(GREEN)Migration history:$(NC)"
	@poetry run alembic history --verbose || echo "$(RED)No migration history$(NC)"

create-migration: ## Создать новую миграцию (использование: make create-migration MESSAGE="описание")
	@if [ -z "$(MESSAGE)" ]; then \
		echo "$(RED)Ошибка: Необходимо указать MESSAGE$(NC)"; \
		echo "Использование: make create-migration MESSAGE=\"описание изменений\""; \
		exit 1; \
	fi
	@echo "$(GREEN)Creating migration: $(MESSAGE)$(NC)"
	poetry run alembic revision --autogenerate -m "$(MESSAGE)"

reset-and-migrate: ## Полный сброс и настройка
	@echo "$(YELLOW)Stopping containers...$(NC)"
	docker-compose down
	@echo "$(YELLOW)Removing postgres volume...$(NC)"
	docker volume rm shared-models_postgres_data 2>/dev/null || true
	@echo "$(GREEN)Starting fresh PostgreSQL...$(NC)"
	docker-compose up -d postgres
	@echo "$(YELLOW)Waiting for PostgreSQL to be ready...$(NC)"
	@until docker exec forum_postgres pg_isready -U docker -d postgres >/dev/null 2>&1; do sleep 1; done
	@echo "$(GREEN)Applying migrations...$(NC)"
	poetry run alembic upgrade head
	@echo "$(GREEN)Database reset complete!$(NC)"

test-relations: ## Запустить тест связей и каскадного удаления
	@echo "$(GREEN)Running relationship tests...$(NC)"
	poetry run python test_relationships.py

test-db: ## Запустить базовый тест подключения
	@echo "$(GREEN)Running database connection test...$(NC)"
	poetry run python test_db.py

clean: ## Очистка кэша и временных файлов
	@echo "$(YELLOW)Cleaning cache and temporary files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	rm -rf .pytest_cache 2>/dev/null || true
	@echo "$(GREEN)Cleanup complete!$(NC)"

logs: ## Показать логи PostgreSQL
	docker-compose logs -f postgres

db-shell: ## Подключиться к PostgreSQL в интерактивном режиме
	docker exec -it forum_postgres psql -U docker -d postgres

db-tables: ## Показать все таблицы
	@echo "$(GREEN)Database tables:$(NC)"
	docker exec forum_postgres psql -U docker -d postgres -c "\dt"

db-extensions: ## Показать установленные расширения
	@echo "$(GREEN)PostgreSQL extensions:$(NC)"
	docker exec forum_postgres psql -U docker -d postgres -c "\dx"

install: ## Установить зависимости
	@echo "$(GREEN)Installing dependencies...$(NC)"
	poetry install

# Docker команды
docker-build: ## Собрать Docker образ на основе pgvector
	@echo "$(GREEN)Building Docker image based on pgvector/pgvector:pg15...$(NC)"
	docker build -t shared-models:postgres .

docker-build-migration: ## Собрать образ для миграций
	@echo "$(GREEN)Building migration Docker image...$(NC)"
	docker build -f Dockerfile.migration -t shared-models:migration .

docker-run-postgres: ## Запустить PostgreSQL с автоматическими миграциями
	@echo "$(GREEN)Running PostgreSQL with shared-models...$(NC)"
	docker run -d \
		--name shared-models-postgres \
		-p 5432:5432 \
		-e POSTGRES_DB=postgres \
		-e POSTGRES_USER=docker \
		-e POSTGRES_PASSWORD=docker \
		-v shared_models_data:/var/lib/postgresql/data \
		shared-models:postgres

docker-run: ## Запустить контейнер интерактивно
	@echo "$(GREEN)Running Docker container...$(NC)"
	docker run --rm -it shared-models:postgres bash

docker-logs: ## Показать логи PostgreSQL контейнера
	@echo "$(GREEN)Showing PostgreSQL logs...$(NC)"
	docker logs -f shared-models-postgres

docker-stop: ## Остановить PostgreSQL контейнер
	@echo "$(YELLOW)Stopping PostgreSQL container...$(NC)"
	docker stop shared-models-postgres 2>/dev/null || true
	docker rm shared-models-postgres 2>/dev/null || true

docker-shell: ## Подключиться к bash в контейнере
	@echo "$(GREEN)Connecting to container shell...$(NC)"
	docker exec -it shared-models-postgres bash

docker-psql: ## Подключиться к PostgreSQL в контейнере
	@echo "$(GREEN)Connecting to PostgreSQL...$(NC)"
	docker exec -it shared-models-postgres psql -U docker -d postgres

docker-test: ## Запустить тесты в контейнере
	@echo "$(GREEN)Running tests in Docker...$(NC)"
	docker exec shared-models-postgres /app/scripts/check-migration-status.sh

docker-clean: ## Очистить Docker образы и кэш
	@echo "$(YELLOW)Cleaning Docker images and cache...$(NC)"
	docker rmi shared-models:latest 2>/dev/null || true
	docker rmi shared-models:migration 2>/dev/null || true
	docker system prune -f

docker-postgres: ## Запустить PostgreSQL в отдельном контейнере
	@echo "$(GREEN)Starting PostgreSQL container...$(NC)"
	docker run -d \
		--name postgres-shared-models \
		-e POSTGRES_DB=postgres \
		-e POSTGRES_USER=docker \
		-e POSTGRES_PASSWORD=docker \
		-p 5432:5432 \
		-v postgres_data_standalone:/var/lib/postgresql/data \
		pgvector/pgvector:pg15

docker-stop-postgres: ## Остановить PostgreSQL контейнер
	@echo "$(YELLOW)Stopping PostgreSQL container...$(NC)"
	docker stop postgres-shared-models 2>/dev/null || true
	docker rm postgres-shared-models 2>/dev/null || true

# Алиас для help по умолчанию
.DEFAULT_GOAL := help
