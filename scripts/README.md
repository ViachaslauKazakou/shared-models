# Scripts для shared-models

Этот каталог содержит скрипты для автоматизации работы с миграциями и базой данных.

## Файлы

### `entrypoint.sh`
Универсальный скрипт инициализации для Docker контейнеров:
- Ожидает готовности базы данных
- Проверяет и применяет миграции
- Выполняет health check
- Запускает основное приложение

**Использование:**
```bash
# В Docker
./scripts/entrypoint.sh python main.py

# Локально
DB_HOST=localhost ./scripts/entrypoint.sh
```

**Переменные окружения:**
- `DB_HOST` - хост БД (по умолчанию: postgres)
- `DB_NAME` - имя БД (по умолчанию: postgres)
- `DB_USER` - пользователь БД (по умолчанию: docker)
- `DB_PASSWORD` - пароль БД (по умолчанию: docker)
- `DB_PORT` - порт БД (по умолчанию: 5432)

### `check-migration-status.sh`
Быстрая проверка статуса миграций и базы данных:
- Проверяет доступность PostgreSQL
- Показывает текущую и доступные миграции
- Проверяет наличие таблиц
- Проверяет pgvector расширение

**Использование:**
```bash
./scripts/check-migration-status.sh
```

## Интеграция с Docker

### Docker Compose
Добавьте в ваш `docker-compose.yml`:

```yaml
services:
  app:
    build: .
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql+psycopg2://docker:docker@postgres:5432/postgres
    entrypoint: ["./scripts/entrypoint.sh"]
    command: ["python", "main.py"]
```

### Отдельный init-контейнер
Используйте `docker-compose.migration.yml` для отдельного контейнера миграций.

## CI/CD

### GitHub Actions
```yaml
- name: Run migrations
  run: |
    docker-compose up -d postgres
    ./scripts/entrypoint.sh echo "Migrations applied"
```

### Makefile интеграция
Все скрипты интегрированы с Makefile:
```bash
make up                 # Использует entrypoint.sh логику
make check-migrations   # Вызывает alembic команды
```

## Логирование

Все скрипты используют цветной вывод:
- 🟢 Зеленый - успешные операции
- 🟡 Желтый - предупреждения
- 🔴 Красный - ошибки

## Безопасность

- Скрипты проверяют доступность БД перед применением миграций
- Таймауты предотвращают бесконечное ожидание
- Корректная обработка сигналов завершения
- Валидация переменных окружения
