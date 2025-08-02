#!/bin/bash
# Скрипт инициализации миграций для PostgreSQL контейнера

set -e

# Переменные
APP_DIR="/app"
DB_NAME="${POSTGRES_DB:-postgres}"
DB_USER="${POSTGRES_USER:-docker}"

echo "🚀 Инициализация миграций shared-models..."

# Ждем пока PostgreSQL полностью запустится
until pg_isready -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; do
    echo "⏳ Ожидание готовности PostgreSQL..."
    sleep 2
done

echo "✅ PostgreSQL готов, применяем миграции..."

# Переходим в директорию приложения
cd "$APP_DIR"

# Применяем миграции
if poetry run alembic upgrade head; then
    echo "✅ Миграции применены успешно!"
    
    # Показываем текущий статус
    echo "📊 Текущий статус миграций:"
    poetry run alembic current
    
    # Показываем созданные таблицы
    echo "📋 Созданные таблицы:"
    psql -U "$DB_USER" -d "$DB_NAME" -c "\dt"
    
else
    echo "❌ Ошибка при применении миграций!"
    exit 1
fi

echo "🎉 Инициализация shared-models завершена!"
