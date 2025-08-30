#!/bin/bash

# Скрипт для применения миграций к удаленной базе данных AWS RDS
# Использует отдельные переменные окружения для удаленной БД

set -e  # Остановить выполнение при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Настройки удаленной БД
REMOTE_DB_HOST="learn-service-test-postgres.cil0uc6gcdkj.us-east-1.rds.amazonaws.com"
REMOTE_DB_PORT="5432"
REMOTE_DB_USER="postgres"
REMOTE_DB_NAME="learnservice"

echo -e "${BLUE}🚀 Скрипт применения миграций к удаленной БД${NC}"
echo -e "${BLUE}=================================================${NC}"
echo -e "${YELLOW}База данных:${NC} ${REMOTE_DB_HOST}:${REMOTE_DB_PORT}/${REMOTE_DB_NAME}"
echo -e "${YELLOW}Пользователь:${NC} ${REMOTE_DB_USER}"
echo ""

# Проверка наличия Poetry
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}❌ Poetry не найден. Установите Poetry для продолжения.${NC}"
    exit 1
fi

# Проверка наличия psql
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ psql не найден. Установите PostgreSQL client для продолжения.${NC}"
    exit 1
fi

# Функция для проверки подключения к БД
check_db_connection() {
    echo -e "${YELLOW}🔍 Проверка подключения к удаленной БД...${NC}"
    
    # Запрос пароля, если не установлен в переменной окружения
    if [ -z "$PGPASSWORD" ]; then
        echo -e "${YELLOW}Введите пароль для пользователя ${REMOTE_DB_USER}:${NC}"
        read -s PGPASSWORD
        export PGPASSWORD
    fi
    
    # Проверка подключения
    if psql -h "$REMOTE_DB_HOST" -p "$REMOTE_DB_PORT" -U "$REMOTE_DB_USER" -d "$REMOTE_DB_NAME" -c "\q" 2>/dev/null; then
        echo -e "${GREEN}✅ Подключение к удаленной БД успешно${NC}"
        return 0
    else
        echo -e "${RED}❌ Не удалось подключиться к удаленной БД${NC}"
        echo -e "${RED}Проверьте параметры подключения и доступность сервера${NC}"
        return 1
    fi
}

# Функция для проверки текущего состояния миграций
check_migration_status() {
    echo -e "${YELLOW}📋 Проверка текущего состояния миграций...${NC}"
    
    # Проверяем текущую версию миграции
    echo -e "${BLUE}Текущая версия миграции в удаленной БД:${NC}"
    poetry run alembic -c alembic.remote.ini current || echo -e "${YELLOW}Миграции еще не применены${NC}"
    
    # Показываем доступные миграции
    echo -e "${BLUE}Доступные миграции:${NC}"
    poetry run alembic -c alembic.remote.ini heads
}

# Функция для применения миграций
apply_migrations() {
    echo -e "${YELLOW}🔄 Применение миграций к удаленной БД...${NC}"
    
    # Применяем миграции используя отдельный конфигурационный файл
    if poetry run alembic -c alembic.remote.ini upgrade head; then
        echo -e "${GREEN}✅ Миграции успешно применены к удаленной БД${NC}"
    else
        echo -e "${RED}❌ Ошибка при применении миграций${NC}"
        exit 1
    fi
}

# Функция для показа таблиц в БД
show_tables() {
    echo -e "${YELLOW}📊 Таблицы в удаленной БД:${NC}"
    psql -h "$REMOTE_DB_HOST" -p "$REMOTE_DB_PORT" -U "$REMOTE_DB_USER" -d "$REMOTE_DB_NAME" -c "\dt"
}

# Главная функция
main() {
    echo -e "${BLUE}Выберите действие:${NC}"
    echo "1) Проверить подключение"
    echo "2) Показать состояние миграций"
    echo "3) Применить миграции"
    echo "4) Показать таблицы"
    echo "5) Выполнить всё (проверка + миграции + таблицы)"
    echo "6) Выход"
    echo ""
    echo -n "Введите номер (1-6): "
    read choice
    
    case $choice in
        1)
            check_db_connection
            ;;
        2)
            if check_db_connection; then
                check_migration_status
            fi
            ;;
        3)
            if check_db_connection; then
                echo -e "${YELLOW}⚠️  Внимание! Вы собираетесь применить миграции к УДАЛЕННОЙ базе данных.${NC}"
                echo -e "${YELLOW}Продолжить? (y/N):${NC}"
                read -r confirm
                if [[ $confirm =~ ^[Yy]$ ]]; then
                    apply_migrations
                    show_tables
                else
                    echo -e "${YELLOW}❌ Операция отменена${NC}"
                fi
            fi
            ;;
        4)
            if check_db_connection; then
                show_tables
            fi
            ;;
        5)
            if check_db_connection; then
                check_migration_status
                echo ""
                echo -e "${YELLOW}⚠️  Внимание! Вы собираетесь применить миграции к УДАЛЕННОЙ базе данных.${NC}"
                echo -e "${YELLOW}Продолжить? (y/N):${NC}"
                read -r confirm
                if [[ $confirm =~ ^[Yy]$ ]]; then
                    apply_migrations
                    echo ""
                    show_tables
                else
                    echo -e "${YELLOW}❌ Операция отменена${NC}"
                fi
            fi
            ;;
        6)
            echo -e "${GREEN}👋 До свидания!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Неверный выбор. Попробуйте снова.${NC}"
            main
            ;;
    esac
}

# Активация Poetry окружения и запуск
echo -e "${YELLOW}🔧 Активация Poetry окружения...${NC}"
if poetry env info &>/dev/null; then
    echo -e "${GREEN}✅ Poetry окружение активировано${NC}"
    echo ""
    main
else
    echo -e "${RED}❌ Ошибка активации Poetry окружения${NC}"
    echo -e "${RED}Убедитесь, что вы находитесь в директории проекта с pyproject.toml${NC}"
    exit 1
fi
