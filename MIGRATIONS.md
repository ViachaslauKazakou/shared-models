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

## Тестирование подключения

Запустите скрипт для проверки подключения и создания тестовых данных:

```bash
poetry run python test_db.py
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
