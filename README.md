# Shared Models

Общие SQLAlchemy модели и Pydantic схемы для микросервисной архитектуры.

## 🚀 Быстрый старт

### Установка как пакет

```bash
# Из Git репозитория
pip install git+https://github.com/ViachaslauKazakou/shared-models.git

# Или через Poetry
poetry add git+https://github.com/ViachaslauKazakou/shared-models.git
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

## 📚 Документация

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

```env
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/db
DB_POOL_SIZE=5
LOG_LEVEL=INFO
```

## 📦 Сборка пакета

```bash
# Сборка
poetry build

# Или использовать скрипт
./build.sh
```

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Сделайте изменения
4. Добавьте тесты
5. Создайте Pull Request
