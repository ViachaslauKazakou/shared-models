# Shared Models

![Release](https://img.shields.io/github/v/release/ViachaslauKazakou/shared-models)
![Build](https://img.shields.io/github/actions/workflo## 📚 Документация

- [Подробная инструкция по использованию](USAGE.md)
- [Работа с миграциями](MIGRATIONS.md)
- [Исправление ошибок отношений](RELATIONSHIP_FIX_GUIDE.md)atus/ViachaslauKazakou/shared-models/test.yml?branch=main)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/github/license/ViachaslauKazakou/shared-models)

Общие SQLAlchemy модели и Pydantic схемы для микросервисной архитектуры.

## 🚀 Быстрый старт

### Установка как пакет

```bash
# Из последнего релиза
pip install git+https://github.com/ViachaslauKazakou/shared-models.git@v0.1.2

# Или через Poetry
poetry add git+https://github.com/ViachaslauKazakou/shared-models.git@v0.1.2

# Из основной ветки (разработка)
pip install git+https://github.com/ViachaslauKazakou/shared-models.git
```

### Использование

```python
from shared_models import User, Topic, Message, UserRole, Status

# Создание пользователя
user = User(
    username="john_doe",
    email="john@example.com",
    user_type=UserRole.user,
    status=Status.active
)
```

## 📋 Содержимое пакета

### Модели
- **User** - пользователи системы
- **Topic** - темы форума
- **Message** - сообщения в темах
- **Embedding** - векторные представления
- **MessageEmbedding** - эмбеддинги сообщений
- **UserKnowledgeRecord** - знания пользователей
- **UserMessageExample** - примеры сообщений

### Схемы
- **UserRole** - роли пользователей
- **Status** - статусы

## 🔧 Разработка

```bash
# Клонирование
git clone https://github.com/ViachaslauKazakou/shared-models.git
cd shared-models

# Установка зависимостей
poetry install

# Применение миграций
poetry run alembic upgrade head

# Тестирование подключения
poetry run python test_db.py
```

## � Устранение проблем

### Проблема с миграциями "no such table: messages"

Если вы видите ошибку типа `sqlalchemy.exc.OperationalError: no such table: messages`, это означает что миграции не синхронизированы с текущим состоянием базы данных.

#### Решение для PostgreSQL (рекомендуется):

1. **Создайте файл .env**:
```bash
# Database Configuration
DATABASE_URL=postgresql+psycopg2://docker:docker@localhost:5433/postgres

# Database Pool Settings
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

2. **Запустите PostgreSQL**:
```bash
docker-compose up -d postgres
```

3. **Сбросьте миграции и создайте базовую**:
```bash
# Удалите старые миграции
rm -f alembic/versions/*.py

# Очистите базу данных
docker exec forum_postgres psql -U docker -d postgres -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Восстановите pgvector
docker exec forum_postgres psql -U docker -d postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Создайте новую базовую миграцию
poetry run alembic revision --autogenerate -m "Initial migration: create all tables"

# Примените миграцию
poetry run alembic upgrade head
```

4. **При необходимости добавьте import pgvector в миграцию**:
Если видите ошибку `NameError: name 'pgvector' is not defined`, добавьте в файл миграции:
```python
import pgvector.sqlalchemy
```

### Проблема с отношениями "UserStatus.user refers to attribute User.status"

Если вы видите ошибку:
```
sqlalchemy.exc.InvalidRequestError: back_populates on relationship 'UserStatus.user' refers to attribute 'User.status' that is not a relationship
```

**Решение:** Обновите shared-models до версии v1.1.2 или выше:

```bash
# Обновите зависимость в вашем проекте
pip install --upgrade git+https://github.com/ViachaslauKazakou/shared-models.git@v1.1.2

# Или пересоберите Docker контейнер
docker-compose build --no-cache your_app
```

Подробности см. в [RELATIONSHIP_FIX_GUIDE.md](RELATIONSHIP_FIX_GUIDE.md)

#### Быстрая команда через Makefile:
```bash
make up  # Запускает PostgreSQL и применяет миграции
```

### Переключение с SQLite на PostgreSQL

Если вы использовали SQLite и хотите перейти на PostgreSQL:

1. Создайте `.env` файл с настройками PostgreSQL (см. выше)
2. Запустите PostgreSQL: `docker-compose up -d postgres`
3. Следуйте инструкциям по сбросу миграций выше

## �📚 Документация

- [Подробная инструкция по использованию](USAGE.md)
- [Работа с миграциями](MIGRATIONS.md)

## 🔄 Миграции

```bash
# Создание миграции
poetry run alembic revision --autogenerate -m "Description"

# Применение миграций  
poetry run alembic upgrade head
```

## ⚙️ Переменные окружения

### PostgreSQL (рекомендуется)
```env
# Database Configuration
DATABASE_URL=postgresql+psycopg2://docker:docker@localhost:5433/postgres

# Database Pool Settings
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### SQLite (для разработки)
```env
DATABASE_URL=sqlite:///./shared_models.db
LOG_LEVEL=INFO
```

## 📦 Сборка пакета

```bash
# Сборка
poetry build

# Или использовать скрипт
./build.sh
```

## 🏷️ Релизы

Проект использует автоматическое создание релизов через GitHub Actions:

### Автоматический релиз:
1. Измените версию в `pyproject.toml`
2. Commit и push в `main`
3. GitHub Actions создаст тег и релиз автоматически

### Ручной релиз:
```bash
# Создание тега
git tag -a v0.1.3 -m "Release version 0.1.3"
git push origin v0.1.3
```

Подробнее см. [.github/RELEASE.md](.github/RELEASE.md)

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Сделайте изменения
4. Добавьте тесты
5. Создайте Pull Request
