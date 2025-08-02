#!/bin/bash
set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Функция для логирования
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Функция для проверки доступности базы данных
wait_for_db() {
    log "Waiting for database to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if python3 -c "
import psycopg2
import sys
try:
    conn = psycopg2.connect(
        host='${DB_HOST:-postgres}',
        database='${DB_NAME:-postgres}', 
        user='${DB_USER:-docker}',
        password='${DB_PASSWORD:-docker}',
        port='${DB_PORT:-5432}'
    )
    conn.close()
    print('Database connection successful!')
except Exception as e:
    print(f'Database connection failed: {e}')
    sys.exit(1)
        " 2>/dev/null; then
            log "Database is ready!"
            return 0
        fi
        
        warn "Database not ready, attempt $attempt/$max_attempts"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    error "Database did not become ready after $max_attempts attempts"
    exit 1
}

# Проверка наличия зависимостей
check_dependencies() {
    log "Checking dependencies..."
    
    if ! command -v poetry &> /dev/null; then
        error "Poetry not found. Please install poetry first."
        exit 1
    fi
    
    if [ ! -f "pyproject.toml" ]; then
        error "pyproject.toml not found. Make sure you're in the project directory."
        exit 1
    fi
    
    log "Installing/updating dependencies..."
    poetry install --no-dev
}

# Применение миграций
apply_migrations() {
    log "Applying database migrations..."
    
    if poetry run alembic upgrade head; then
        log "Migrations applied successfully!"
    else
        error "Migration failed!"
        exit 1
    fi
}

# Проверка статуса миграций
check_migrations() {
    log "Checking migration status..."
    
    # Получаем текущую версию миграции
    current=$(poetry run alembic current 2>/dev/null | grep -o '[a-f0-9]\{12\}' | head -1)
    head=$(poetry run alembic heads 2>/dev/null | grep -o '[a-f0-9]\{12\}' | head -1)
    
    if [ -z "$current" ]; then
        warn "No current migration found. Database might be empty."
        apply_migrations
    elif [ "$current" = "$head" ]; then
        log "Database is up to date (revision: $current)"
    else
        warn "Database needs migration. Current: ${current:-none}, Head: ${head:-none}"
        apply_migrations
    fi
}

# Проверка здоровья базы данных
health_check() {
    log "Performing health check..."
    
    # Проверяем pgvector расширение
    if docker exec forum_postgres psql -U docker -d postgres -c "SELECT 1 FROM pg_extension WHERE extname = 'vector';" >/dev/null 2>&1; then
        log "pgvector extension is installed"
    else
        warn "pgvector extension not found"
    fi
    
    # Проверяем основные таблицы
    local tables=("users" "topics" "messages" "message_embeddings" "embeddings")
    for table in "${tables[@]}"; do
        if docker exec forum_postgres psql -U docker -d postgres -c "\d $table" >/dev/null 2>&1; then
            log "Table '$table' exists"
        else
            warn "Table '$table' not found"
        fi
    done
}

# Основная логика
main() {
    log "Starting shared-models initialization..."
    
    # Проверяем переменные окружения
    log "Environment variables:"
    echo "  DB_HOST: ${DB_HOST:-postgres}"
    echo "  DB_NAME: ${DB_NAME:-postgres}"
    echo "  DB_USER: ${DB_USER:-docker}"
    echo "  DB_PORT: ${DB_PORT:-5432}"
    
    # Основная последовательность инициализации
    check_dependencies
    wait_for_db
    check_migrations
    health_check
    
    log "Initialization completed successfully!"
    
    # Если переданы аргументы, выполняем их как команду
    if [ $# -gt 0 ]; then
        log "Executing command: $*"
        exec "$@"
    else
        log "No command specified, keeping container running..."
        tail -f /dev/null
    fi
}

# Обработка сигналов для корректного завершения
trap 'log "Received termination signal, shutting down..."; exit 0' SIGTERM SIGINT

# Запуск основной логики
main "$@"
