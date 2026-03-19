#!/bin/bash

# Скрипт для резервного копирования и восстановления удаленной БД AWS RDS
# Поддерживает гибкие параметры для развертывания на новых инстансах

set -e  # Остановить выполнение при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Загрузить переменные из .env.backup если файл существует
if [ -f ".env.backup" ]; then
    echo -e "${BLUE}📄 Загружаю переменные из .env.backup${NC}"
    set -a
    source .env.backup
    set +a
    echo -e "${GREEN}✅ Переменные окружения загружены${NC}"
    echo ""
fi

# Директория для хранения бэкапов
BACKUP_DIR="${BACKUP_DIR:-./backups}"
mkdir -p "$BACKUP_DIR"

# Параметры исходной БД (по умолчанию)
SOURCE_DB_HOST="${SOURCE_DB_HOST:-simple-ec2-db.cecurbs9fk6o.us-east-1.rds.amazonaws.com}"
SOURCE_DB_PORT="${SOURCE_DB_PORT:-5432}"
SOURCE_DB_USER="${SOURCE_DB_USER:-postgres}"
SOURCE_DB_NAME="${SOURCE_DB_NAME:-learnservicedatabase}"
SOURCE_DB_PASSWORD="${SOURCE_DB_PASSWORD:-vk-db-postgres}"

# Параметры целевой БД (для восстановления)
TARGET_DB_HOST="${TARGET_DB_HOST:-}"
TARGET_DB_PORT="${TARGET_DB_PORT:-5432}"
TARGET_DB_USER="${TARGET_DB_USER:-postgres}"
TARGET_DB_NAME="${TARGET_DB_NAME:-learnservicedatabase}"
TARGET_DB_PASSWORD="${TARGET_DB_PASSWORD:-}"

echo -e "${BLUE}🗄️  Скрипт резервного копирования удаленной БД${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo ""

# Проверка наличия утилит
check_requirements() {
    local required_tools=("psql" "pg_dump" "pg_restore")
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            echo -e "${RED}❌ Не найден $tool. Установите PostgreSQL client для продолжения.${NC}"
            exit 1
        fi
    done
    
    echo -e "${GREEN}✅ Все необходимые утилиты найдены (psql, pg_dump, pg_restore)${NC}"
}

# Проверка подключения к БД
check_db_connection() {
    local host=$1
    local port=$2
    local user=$3
    local db=$4
    local password=$5
    
    echo -e "${YELLOW}🔍 Проверка подключения к ${host}:${port}/${db}...${NC}"
    
    export PGPASSWORD="$password"
    
    if psql -h "$host" -p "$port" -U "$user" -d "$db" -c "\q" 2>/dev/null; then
        echo -e "${GREEN}✅ Подключение успешно${NC}"
        return 0
    else
        echo -e "${RED}❌ Не удалось подключиться${NC}"
        echo -e "${RED}Параметры: $user@$host:$port/$db${NC}"
        return 1
    fi
}

# Создание полного бэкапа в формате custom (сжатый)
backup_database() {
    echo -e "${YELLOW}📦 Создание резервной копии БД...${NC}"
    
    # Проверяем подключение
    if ! check_db_connection "$SOURCE_DB_HOST" "$SOURCE_DB_PORT" "$SOURCE_DB_USER" "$SOURCE_DB_NAME" "$SOURCE_DB_PASSWORD"; then
        echo -e "${RED}Не удалось подключиться к исходной БД${NC}"
        return 1
    fi
    
    # Генерируем имя файла с датой
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="${BACKUP_DIR}/backup_${timestamp}.dump"
    
    echo -e "${BLUE}Создаю дамп в ${backup_file}...${NC}"
    
    export PGPASSWORD="$SOURCE_DB_PASSWORD"
    
    if pg_dump -h "$SOURCE_DB_HOST" -p "$SOURCE_DB_PORT" -U "$SOURCE_DB_USER" \
               -d "$SOURCE_DB_NAME" \
               -F c \
               -v \
               -f "$backup_file" 2>&1 | grep -v "^pg_dump:"; then
        
        local file_size=$(du -h "$backup_file" | cut -f1)
        echo -e "${GREEN}✅ Бэкап создан: ${backup_file} (${file_size})${NC}"
        
        # Показываем контрольную сумму для проверки целостности
        local checksum=$(md5sum "$backup_file" | awk '{print $1}')
        echo -e "${BLUE}MD5: ${checksum}${NC}"
        
        echo "$backup_file|$checksum" >> "${BACKUP_DIR}/.backup_manifest"
        
        return 0
    else
        echo -e "${RED}❌ Ошибка при создании бэкапа${NC}"
        rm -f "$backup_file"
        return 1
    fi
}

# Создание текстового дампа (SQL)
backup_database_sql() {
    echo -e "${YELLOW}📄 Создание текстового дампа БД...${NC}"
    
    # Проверяем подключение
    if ! check_db_connection "$SOURCE_DB_HOST" "$SOURCE_DB_PORT" "$SOURCE_DB_USER" "$SOURCE_DB_NAME" "$SOURCE_DB_PASSWORD"; then
        echo -e "${RED}Не удалось подключиться к исходной БД${NC}"
        return 1
    fi
    
    # Генерируем имя файла с датой
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="${BACKUP_DIR}/backup_${timestamp}.sql"
    
    echo -e "${BLUE}Создаю SQL дамп в ${backup_file}...${NC}"
    
    export PGPASSWORD="$SOURCE_DB_PASSWORD"
    
    if pg_dump -h "$SOURCE_DB_HOST" -p "$SOURCE_DB_PORT" -U "$SOURCE_DB_USER" \
               -d "$SOURCE_DB_NAME" \
               -v \
               -f "$backup_file"; then
        
        local file_size=$(du -h "$backup_file" | cut -f1)
        echo -e "${GREEN}✅ SQL дамп создан: ${backup_file} (${file_size})${NC}"
        
        return 0
    else
        echo -e "${RED}❌ Ошибка при создании SQL дампа${NC}"
        rm -f "$backup_file"
        return 1
    fi
}

# Восстановление из бэкапа
restore_database() {
    echo -e "${YELLOW}🔄 Восстановление БД из бэкапа${NC}"
    
    # Список доступных бэкапов
    echo -e "${BLUE}Доступные бэкапы:${NC}"
    local backups=($(find "$BACKUP_DIR" -maxdepth 1 -name "backup_*.dump" -o -name "backup_*.sql" | sort -r))
    
    if [ ${#backups[@]} -eq 0 ]; then
        echo -e "${RED}❌ Бэкапы не найдены${NC}"
        return 1
    fi
    
    for i in "${!backups[@]}"; do
        echo "$((i+1))) ${backups[$i]}"
    done
    
    echo ""
    echo -n "Выберите номер бэкапа (1-${#backups[@]}): "
    read backup_choice
    
    if [[ ! "$backup_choice" =~ ^[0-9]+$ ]] || [ "$backup_choice" -lt 1 ] || [ "$backup_choice" -gt ${#backups[@]} ]; then
        echo -e "${RED}❌ Неверный выбор${NC}"
        return 1
    fi
    
    local selected_backup="${backups[$((backup_choice-1))]}"
    
    echo -e "${YELLOW}Выбран бэкап: ${selected_backup}${NC}"
    echo ""
    
    # Ввод параметров целевой БД
    echo -e "${BLUE}Введите параметры целевой БД:${NC}"
    
    echo -n "Хост (по умолчанию: $TARGET_DB_HOST): "
    read target_host
    target_host="${target_host:-$TARGET_DB_HOST}"
    
    echo -n "Порт (по умолчанию: $TARGET_DB_PORT): "
    read target_port
    target_port="${target_port:-$TARGET_DB_PORT}"
    
    echo -n "Пользователь (по умолчанию: $TARGET_DB_USER): "
    read target_user
    target_user="${target_user:-$TARGET_DB_USER}"
    
    echo -n "Название БД (по умолчанию: $TARGET_DB_NAME): "
    read target_db
    target_db="${target_db:-$TARGET_DB_NAME}"
    
    echo -n "Пароль: "
    read -s target_password
    echo ""
    
    # Проверка подключения к целевой БД
    if ! check_db_connection "$target_host" "$target_port" "$target_user" "$target_db" "$target_password"; then
        echo -e "${RED}Не удалось подключиться к целевой БД${NC}"
        return 1
    fi
    
    # Предупреждение
    echo -e "${RED}⚠️  ВНИМАНИЕ! Это перезапишет данные в $target_user@$target_host:$target_port/$target_db${NC}"
    echo -e "${YELLOW}Вы уверены? (yes/no): ${NC}"
    read -r confirm
    
    if [[ "$confirm" != "yes" ]]; then
        echo -e "${YELLOW}❌ Восстановление отменено${NC}"
        return 0
    fi
    
    # Определяем формат бэкапа по расширению файла
    if [[ "$selected_backup" == *.dump ]]; then
        # Восстановление из custom формата
        echo -e "${BLUE}Начинаю восстановление из бэкапа (формат custom)...${NC}"
        
        export PGPASSWORD="$target_password"
        
        if pg_restore -h "$target_host" -p "$target_port" -U "$target_user" \
                      -d "$target_db" \
                      -v \
                      --no-owner \
                      --role="$target_user" \
                      "$selected_backup" 2>&1 | grep -v "^pg_restore:"; then
            
            echo -e "${GREEN}✅ Восстановление завершено${NC}"
            return 0
        else
            echo -e "${RED}❌ Ошибка при восстановлении${NC}"
            return 1
        fi
    else
        # Восстановление из SQL формата
        echo -e "${BLUE}Начинаю восстановление из бэкапа (формат SQL)...${NC}"
        
        export PGPASSWORD="$target_password"
        
        if psql -h "$target_host" -p "$target_port" -U "$target_user" \
                -d "$target_db" \
                -f "$selected_backup" > /dev/null 2>&1; then
            
            echo -e "${GREEN}✅ Восстановление завершено${NC}"
            return 0
        else
            echo -e "${RED}❌ Ошибка при восстановлении${NC}"
            return 1
        fi
    fi
}

# Список бэкапов
list_backups() {
    echo -e "${BLUE}📋 Список доступных бэкапов:${NC}"
    
    if ! ls -lh "$BACKUP_DIR"/backup_* 2>/dev/null | awk '{print $9, "(" $5 ")"}'; then
        echo -e "${YELLOW}Бэкапы не найдены${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}Информация о бэкапах:${NC}"
    local total_size=$(du -sh "$BACKUP_DIR" | cut -f1)
    echo "Всего займат бэкапы: $total_size"
    echo "Директория: $BACKUP_DIR"
}

# Удаление старого бэкапа
delete_backup() {
    echo -e "${YELLOW}🗑️  Удаление бэкапа${NC}"
    
    # Список доступных бэкапов
    local backups=($(ls -t "$BACKUP_DIR"/backup_* 2>/dev/null | sort -r))
    
    if [ ${#backups[@]} -eq 0 ]; then
        echo -e "${RED}❌ Бэкапы не найдены${NC}"
        return 1
    fi
    
    for i in "${!backups[@]}"; do
        local size=$(du -h "${backups[$i]}" | cut -f1)
        echo "$((i+1))) ${backups[$i]} ($size)"
    done
    
    echo ""
    echo -n "Выберите номер бэкапа для удаления (1-${#backups[@]}): "
    read backup_choice
    
    if [[ ! "$backup_choice" =~ ^[0-9]+$ ]] || [ "$backup_choice" -lt 1 ] || [ "$backup_choice" -gt ${#backups[@]} ]; then
        echo -e "${RED}❌ Неверный выбор${NC}"
        return 1
    fi
    
    local selected_backup="${backups[$((backup_choice-1))]}"
    
    echo -e "${YELLOW}⚠️  Удалить ${selected_backup}? (yes/no): ${NC}"
    read -r confirm
    
    if [[ "$confirm" == "yes" ]]; then
        rm -f "$selected_backup"
        echo -e "${GREEN}✅ Бэкап удален${NC}"
    else
        echo -e "${YELLOW}❌ Удаление отменено${NC}"
    fi
}

# Проверка целостности бэкапа
verify_backup() {
    echo -e "${YELLOW}🔐 Проверка целостности бэкапа${NC}"
    
    # Список доступных бэкапов
    local backups=($(find "$BACKUP_DIR" -maxdepth 1 -name "backup_*.dump" | sort -r))
    
    if [ ${#backups[@]} -eq 0 ]; then
        echo -e "${RED}❌ Бэкапы в формате custom не найдены${NC}"
        return 1
    fi
    
    for i in "${!backups[@]}"; do
        echo "$((i+1))) ${backups[$i]}"
    done
    
    echo ""
    echo -n "Выберите номер бэкапа для проверки (1-${#backups[@]}): "
    read backup_choice
    
    if [[ ! "$backup_choice" =~ ^[0-9]+$ ]] || [ "$backup_choice" -lt 1 ] || [ "$backup_choice" -gt ${#backups[@]} ]; then
        echo -e "${RED}❌ Неверный выбор${NC}"
        return 1
    fi
    
    local selected_backup="${backups[$((backup_choice-1))]}"
    
    echo -e "${BLUE}Проверяю ${selected_backup}...${NC}"
    
    if pg_restore -f /dev/null "$selected_backup" 2>&1 | grep -q "error"; then
        echo -e "${RED}❌ Бэкап повреждён${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Бэкап в порядке${NC}"
        
        # Показываем информацию о бэкапе
        echo -e "${BLUE}Информация о бэкапе:${NC}"
        pg_restore -l "$selected_backup" | head -20
        echo "..."
        
        return 0
    fi
}

# Главное меню
main() {
    echo -e "${BLUE}Выберите действие:${NC}"
    echo "1) Создать бэкап (custom формат - сжатый)"
    echo "2) Создать SQL дамп (текстовый)"
    echo "3) Восстановить из бэкапа"
    echo "4) Показать список бэкапов"
    echo "5) Проверить целостность бэкапа"
    echo "6) Удалить бэкап"
    echo "7) Выход"
    echo ""
    echo -n "Введите номер (1-7): "
    read choice
    
    case $choice in
        1)
            backup_database
            ;;
        2)
            backup_database_sql
            ;;
        3)
            restore_database
            ;;
        4)
            list_backups
            ;;
        5)
            verify_backup
            ;;
        6)
            delete_backup
            ;;
        7)
            echo -e "${GREEN}👋 До свидания!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Неверный выбор. Попробуйте снова.${NC}"
            main
            ;;
    esac
    
    echo ""
    main
}

# Проверка требований и запуск
check_requirements
echo ""
main
