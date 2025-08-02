#!/bin/bash

# Скрипт для сборки и тестирования Docker образов

set -e

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Функции логирования
log() { echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"; }
warn() { echo -e "${YELLOW}[$(date +'%H:%M:%S')] $1${NC}"; }
error() { echo -e "${RED}[$(date +'%H:%M:%S')] $1${NC}"; }
info() { echo -e "${BLUE}[$(date +'%H:%M:%S')] $1${NC}"; }

# Переменные
IMAGE_NAME="shared-models"
VERSION=${1:-"latest"}

# Функция для проверки Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker не установлен или недоступен"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker демон не запущен"
        exit 1
    fi
    
    log "Docker готов к использованию"
}

# Функция сборки образа
build_image() {
    local target=${1:-"production"}
    local tag="${IMAGE_NAME}:${VERSION}-${target}"
    
    info "Сборка образа: $tag"
    
    if [ "$target" = "development" ]; then
        docker build -f Dockerfile.prod --target development -t "$tag" .
    elif [ "$target" = "production" ]; then
        docker build -f Dockerfile.prod --target production -t "$tag" .
    elif [ "$target" = "testing" ]; then
        docker build -f Dockerfile.prod --target testing -t "$tag" .
    else
        docker build -t "$tag" .
    fi
    
    log "Образ $tag собран успешно"
}

# Функция тестирования образа
test_image() {
    local tag="${IMAGE_NAME}:${VERSION}-${1:-production}"
    
    info "Тестирование образа: $tag"
    
    # Проверка что образ запускается
    if docker run --rm "$tag" echo "Container test OK" &> /dev/null; then
        log "Базовый тест контейнера прошел успешно"
    else
        error "Базовый тест контейнера провалился"
        return 1
    fi
    
    # Проверка импорта модулей
    if docker run --rm "$tag" poetry run python -c "import shared_models; print('Import test OK')" &> /dev/null; then
        log "Тест импорта модулей прошел успешно"
    else
        error "Тест импорта модулей провалился"
        return 1
    fi
}

# Функция очистки старых образов
cleanup() {
    info "Очистка старых образов..."
    
    # Удаление старых версий
    docker images "${IMAGE_NAME}" --format "table {{.Repository}}:{{.Tag}}" | grep -v "TAG" | grep -v "$VERSION" | xargs -r docker rmi || true
    
    # Очистка неиспользуемых образов
    docker system prune -f
    
    log "Очистка завершена"
}

# Функция отображения информации об образах
show_images() {
    info "Доступные образы shared-models:"
    docker images "${IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
}

# Основная функция
main() {
    echo -e "${BLUE}=== Docker Build Script для shared-models ===${NC}\n"
    
    # Проверка аргументов
    case "${2:-all}" in
        "dev"|"development")
            TARGET="development"
            ;;
        "prod"|"production")
            TARGET="production"
            ;;
        "test"|"testing")
            TARGET="testing"
            ;;
        "all")
            TARGET="all"
            ;;
        *)
            warn "Неизвестный target: $2. Используем 'all'"
            TARGET="all"
            ;;
    esac
    
    check_docker
    
    if [ "$TARGET" = "all" ]; then
        log "Сборка всех вариантов образов..."
        build_image "development"
        build_image "production"
        build_image "testing"
        
        log "Тестирование образов..."
        test_image "development"
        test_image "production"
        test_image "testing"
    else
        log "Сборка образа для target: $TARGET"
        build_image "$TARGET"
        
        log "Тестирование образа..."
        test_image "$TARGET"
    fi
    
    show_images
    
    # Опциональная очистка
    read -p "Выполнить очистку старых образов? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cleanup
    fi
    
    log "Сборка завершена успешно!"
}

# Справка
show_help() {
    echo "Использование: $0 [VERSION] [TARGET]"
    echo ""
    echo "Аргументы:"
    echo "  VERSION   Версия образа (по умолчанию: latest)"
    echo "  TARGET    Цель сборки: dev|prod|test|all (по умолчанию: all)"
    echo ""
    echo "Примеры:"
    echo "  $0                    # Собрать все образы с версией 'latest'"
    echo "  $0 v1.0.0            # Собрать все образы с версией 'v1.0.0'"
    echo "  $0 latest prod       # Собрать только production образ"
    echo "  $0 dev-branch dev    # Собрать только development образ"
}

# Обработка аргументов
if [[ "${1}" == "--help" ]] || [[ "${1}" == "-h" ]]; then
    show_help
    exit 0
fi

# Запуск основной функции
main "$@"
