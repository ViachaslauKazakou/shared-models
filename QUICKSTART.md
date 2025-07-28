# 📋 Краткая инструкция по использованию shared-models как пакета

## 🎯 Цель
Пакет `shared-models` предназначен для переиспользования общих SQLAlchemy моделей и схем между различными микросервисами.

## ⚡ Быстрый старт

### 1. Установка пакета

**Вариант A: Из Git репозитория (рекомендуемый)**
```bash
pip install git+https://github.com/ViachaslauKazakou/shared-models.git
```

**Вариант B: Локальная установка wheel файла**
```bash
pip install shared_models-0.1.1-py3-none-any.whl
```

**Вариант C: Через Poetry**
```bash
poetry add git+https://github.com/ViachaslauKazakou/shared-models.git
```

### 2. Использование в коде

```python
# Импорт моделей
from shared_models import User, Topic, Message, UserRole, Status

# Создание пользователя
user = User(
    username="john_doe",
    email="john@example.com", 
    user_type=UserRole.user,
    status=Status.active
)
```

### 3. Настройка БД в вашем проекте

```python
# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 4. Применение миграций

```bash
# Создание миграции
alembic revision --autogenerate -m "Add shared models"

# Применение
alembic upgrade head
```

## 📚 Доступные модели

- **User** - пользователи (username, email, user_type, status)
- **Topic** - темы форума (title, description, user_id) 
- **Message** - сообщения (content, author_name, topic_id, user_id)
- **Embedding** - векторные представления (content, embedding)
- **MessageEmbedding** - эмбеддинги сообщений
- **UserKnowledgeRecord** - знания пользователей
- **UserMessageExample** - примеры сообщений

## 📚 Документация

- **[USAGE.md](USAGE.md)** - Полная документация по использованию
- **[EXAMPLES.md](EXAMPLES.md)** - Примеры для FastAPI, Django и других фреймворков
- **[MIGRATIONS.md](MIGRATIONS.md)** - Работа с миграциями Alembic

## 🔄 Обновление

```bash
pip install --upgrade git+https://github.com/ViachaslauKazakou/shared-models.git
```

## ✅ Готово!

Теперь вы можете использовать общие модели в любом своем проекте. Пакет автоматически установит все необходимые зависимости (SQLAlchemy, Alembic, pgvector и др.).
