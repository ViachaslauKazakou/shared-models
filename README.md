# Shared Models

![Release](https://img.shields.io/github/v/release/ViachaslauKazakou/shared-models)
![Build](https://img.shields.io/github/actions/workflow/status/ViachaslauKazakou/shared-models/test.yml?branch=main)
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
