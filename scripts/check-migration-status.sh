#!/bin/bash

# Скрипт для быстрой проверки статуса миграций

set -e

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Shared Models Migration Status ===${NC}\n"

# Проверка доступности базы данных
echo -e "${YELLOW}Checking database connection...${NC}"
if docker exec forum_postgres pg_isready -U docker -d postgres >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Database is accessible${NC}"
else
    echo -e "${RED}✗ Database is not accessible${NC}"
    exit 1
fi

# Текущая миграция
echo -e "\n${YELLOW}Current migration:${NC}"
current=$(poetry run alembic current 2>/dev/null || echo "No migration applied")
echo "  $current"

# Доступные миграции
echo -e "\n${YELLOW}Available migrations (head):${NC}"
head=$(poetry run alembic heads 2>/dev/null || echo "No migrations found")
echo "  $head"

# Проверка статуса
echo -e "\n${YELLOW}Migration status:${NC}"
if [[ "$current" == *"(head)"* ]]; then
    echo -e "${GREEN}✓ Database is up to date${NC}"
elif [[ "$current" == "No migration applied" ]]; then
    echo -e "${RED}✗ No migrations applied to database${NC}"
    echo -e "${YELLOW}  Run: poetry run alembic upgrade head${NC}"
else
    echo -e "${YELLOW}⚠ Database may need updates${NC}"
    echo -e "${YELLOW}  Run: poetry run alembic upgrade head${NC}"
fi

# Проверка таблиц
echo -e "\n${YELLOW}Database tables:${NC}"
if docker exec forum_postgres psql -U docker -d postgres -c "\dt" 2>/dev/null | grep -q "public"; then
    table_count=$(docker exec forum_postgres psql -U docker -d postgres -c "\dt" 2>/dev/null | grep "public" | wc -l)
    echo -e "${GREEN}✓ Found $table_count tables${NC}"
else
    echo -e "${RED}✗ No tables found${NC}"
fi

# Проверка pgvector
echo -e "\n${YELLOW}pgvector extension:${NC}"
if docker exec forum_postgres psql -U docker -d postgres -c "SELECT 1 FROM pg_extension WHERE extname = 'vector';" >/dev/null 2>&1; then
    version=$(docker exec forum_postgres psql -U docker -d postgres -c "SELECT extversion FROM pg_extension WHERE extname = 'vector';" -t 2>/dev/null | xargs)
    echo -e "${GREEN}✓ pgvector v$version is installed${NC}"
else
    echo -e "${RED}✗ pgvector extension not found${NC}"
fi

echo -e "\n${BLUE}=== End of Status Report ===${NC}"
