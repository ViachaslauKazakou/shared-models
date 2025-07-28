# Инструкция по использованию shared-models как пакета

## Обзор

`shared-models` - это Python пакет, содержащий общие SQLAlchemy модели и Pydantic схемы для микросервисной архитектуры. Пакет включает в себя модели для пользователей, тем, сообщений, эмбеддингов и системы миграций Alembic.

## Модели и схемы

### Основные модели:
- **User** - пользователи системы
- **Topic** - темы форума  
- **Message** - сообщения в темах
- **Embedding** - векторные представления
- **MessageEmbedding** - эмбеддинги сообщений
- **UserKnowledgeRecord** - знания пользователей
- **UserMessageExample** - примеры сообщений пользователей

### Схемы:
- **UserRole** - роли пользователей (admin, user, ai_bot, mixed, mentor, mentee)
- **Status** - статусы (pending, active, disabled, blocked, deleted)

## Способы установки

### 1. Установка из Git репозитория (рекомендуемый)

#### Через Poetry
```bash
# Добавить зависимость в ваш проект
poetry add git+https://github.com/ViachaslauKazakou/shared-models.git

# Или с указанием конкретной ветки/тега
poetry add git+https://github.com/ViachaslauKazakou/shared-models.git@main
```

#### Через pip
```bash
# Установка из Git
pip install git+https://github.com/ViachaslauKazakou/shared-models.git

# Или с SSH (если настроен SSH ключ)
pip install git+ssh://git@github.com/ViachaslauKazakou/shared-models.git
```

#### Через requirements.txt
```text
# В файле requirements.txt
git+https://github.com/ViachaslauKazakou/shared-models.git
```

### 2. Локальная установка для разработки

```bash
# Клонирование репозитория
git clone https://github.com/ViachaslauKazakou/shared-models.git
cd shared-models

# Установка в режиме разработки
pip install -e .

# Или через Poetry
poetry install
```

### 3. Установка конкретной версии

```bash
# По тегу версии
pip install git+https://github.com/ViachaslauKazakou/shared-models.git@v0.1.0

# По коммиту
pip install git+https://github.com/ViachaslauKazakou/shared-models.git@abc123def
```

## Использование в вашем проекте

### 1. Базовая настройка

```python
# В вашем проекте создайте файл database.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Импорт моделей
from shared_models import Base, engine as shared_engine, SessionLocal as SharedSessionLocal

# Создание своего движка с вашими настройками
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/mydb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функция для получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 2. Импорт и использование моделей

```python
# Импорт моделей
from shared_models import (
    User, Topic, Message, 
    UserRole, Status,
    Embedding, MessageEmbedding,
    UserKnowledgeRecord, UserMessageExample
)

# Использование в вашем коде
def create_user(db_session, username: str, email: str):
    user = User(
        username=username,
        email=email,
        user_type=UserRole.user,
        status=Status.pending
    )
    db_session.add(user)
    db_session.commit()
    return user

def get_user_topics(db_session, user_id: int):
    return db_session.query(Topic).filter(Topic.user_id == user_id).all()
```

### 3. Настройка миграций в вашем проекте

#### Создание alembic.ini в вашем проекте:
```ini
[alembic]
script_location = alembic
file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s
prepend_sys_path = .

sqlalchemy.url = postgresql://user:pass@localhost/mydb

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

#### Создание env.py для Alembic:
```python
import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Импорт моделей shared-models
from shared_models.models import Base
from shared_models.models import (
    User, Topic, Message, 
    Embedding, MessageEmbedding,
    UserKnowledgeRecord, UserMessageExample
)

# Импорт ваших локальных моделей (если есть)
# from myapp.models import MyModel

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 4. Применение миграций

```bash
# Инициализация Alembic (если еще не сделано)
alembic init alembic

# Создание миграции
alembic revision --autogenerate -m "Initial migration with shared models"

# Применение миграций
alembic upgrade head
```

## Примеры использования

### FastAPI приложение

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from shared_models import User, Topic, Message, UserRole, Status
from .database import get_db

app = FastAPI()

@app.post("/users/")
def create_user(username: str, email: str, db: Session = Depends(get_db)):
    user = User(
        username=username,
        email=email,
        user_type=UserRole.user,
        status=Status.pending
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.get("/users/{user_id}/topics")
def get_user_topics(user_id: int, db: Session = Depends(get_db)):
    topics = db.query(Topic).filter(Topic.user_id == user_id).all()
    return topics
```

### Django приложение

```python
# В settings.py добавьте shared_models в INSTALLED_APPS
INSTALLED_APPS = [
    # ... ваши приложения
    'shared_models',
]

# Использование в views.py
from django.shortcuts import render
from shared_models.models import User, Topic

def user_topics(request, user_id):
    user = User.objects.get(id=user_id)
    topics = Topic.objects.filter(user_id=user_id)
    return render(request, 'topics.html', {'user': user, 'topics': topics})
```

## Переменные окружения

Создайте файл `.env` в вашем проекте:

```env
# Database
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/yourdb

# Pool settings
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## Обновление пакета

```bash
# Обновление до последней версии
pip install --upgrade git+https://github.com/ViachaslauKazakou/shared-models.git

# Или через Poetry
poetry update shared-models
```

## Работа с векторными данными (pgvector)

```python
from shared_models import Embedding, MessageEmbedding
import numpy as np

# Создание эмбеддинга
embedding_vector = np.random.rand(1536).tolist()  # Пример вектора

embedding = Embedding(
    content="Текст для эмбеддинга",
    embedding=embedding_vector,
    extra_metadata={"source": "openai", "model": "text-embedding-ada-002"}
)

db.add(embedding)
db.commit()
```

## Troubleshooting

### Проблемы с установкой
1. Убедитесь, что у вас есть доступ к репозиторию
2. Проверьте наличие git на вашей системе
3. Для приватных репозиториев настройте SSH ключи

### Проблемы с миграциями
1. Убедитесь, что все модели импортированы в env.py
2. Проверьте правильность DATABASE_URL
3. Убедитесь, что база данных существует

### Проблемы с pgvector
1. Установите расширение в PostgreSQL: `CREATE EXTENSION vector;`
2. Убедитесь, что версия PostgreSQL поддерживает pgvector

## Поддержка

Для вопросов и предложений создавайте issues в репозитории:
https://github.com/ViachaslauKazakou/shared-models/issues

## Создание релизов (для разработчиков пакета)

### Подготовка к релизу

1. **Обновите версию в pyproject.toml:**
```toml
[tool.poetry]
version = "0.1.2"  # Новая версия
```

2. **Создайте запись в CHANGELOG.md:**
```markdown
## [0.1.2] - 2025-07-28
### Added
- Новая функциональность
### Changed  
- Изменения в существующем коде
### Fixed
- Исправленные ошибки
```

3. **Убедитесь, что все тесты проходят:**
```bash
poetry run python test_package.py
poetry run python test_db.py
```

### Создание релиза

1. **Закоммитьте все изменения:**
```bash
git add .
git commit -m "Release v0.1.2: описание изменений"
```

2. **Создайте и запушьте тег:**
```bash
# Создать тег локально
git tag v0.1.2

# Проверить создание тега
git tag -l

# Запушить основную ветку
git push origin main

# Запушить тег
git push origin v0.1.2
```

3. **Пересоберите пакет (опционально):**
```bash
# Очистить старые сборки
rm -rf dist/*

# Собрать новую версию
poetry build

# Проверить созданные файлы
ls -la dist/
```

### Исправление ошибок при создании тега

Если получили ошибку `error: src refspec v0.1.2 does not match any`:

```bash
# Удалить локальный тег (если существует)
git tag -d v0.1.2

# Удалить удаленный тег (если существует) 
git push origin :refs/tags/v0.1.2

# Создать тег заново
git tag v0.1.2

# Запушить тег
git push origin v0.1.2
```

### Использование конкретных версий

После создания релиза пользователи могут устанавливать конкретную версию:

```bash
# Poetry
poetry add git+https://github.com/ViachaslauKazakou/shared-models.git@v0.1.2

# pip
pip install git+https://github.com/ViachaslauKazakou/shared-models.git@v0.1.2

# requirements.txt
git+https://github.com/ViachaslauKazakou/shared-models.git@v0.1.2

# pyproject.toml
[tool.poetry.dependencies]
shared-models = {git = "https://github.com/ViachaslauKazakou/shared-models.git", tag = "v0.1.2"}
```

### Рекомендации по версионированию

Используйте [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0) - Breaking changes (несовместимые изменения API)
- **MINOR** (0.X.0) - Новая функциональность (обратно совместимая)  
- **PATCH** (0.0.X) - Исправления ошибок (обратно совместимые)

**Примеры:**
- `v0.1.0` → `v0.1.1` - исправление ошибок
- `v0.1.1` → `v0.2.0` - новые модели или поля
- `v0.2.0` → `v1.0.0` - breaking changes в API

### Автоматизация релизов

Создайте скрипт для автоматизации релизов:

```bash
#!/bin/bash
# release.sh

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 0.1.2"
    exit 1
fi

VERSION=$1
TAG="v$VERSION"

echo "🚀 Создание релиза $TAG"

# Обновить версию в pyproject.toml
sed -i.bak "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml
rm pyproject.toml.bak

# Коммит и тег
git add pyproject.toml
git commit -m "Release $TAG"
git tag $TAG

# Пуш
git push origin main
git push origin $TAG

# Сборка пакета
poetry build

echo "✅ Релиз $TAG создан успешно!"
echo "📦 Файлы сборки доступны в директории dist/"
```

Использование скрипта:
```bash
chmod +x release.sh
./release.sh 0.1.2
```
