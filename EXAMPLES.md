# Примеры конфигурации для различных проектов

## FastAPI проект

### pyproject.toml
```toml
[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
shared-models = {git = "https://github.com/ViachaslauKazakou/shared-models.git"}
```

### app/database.py
```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared_models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/mydb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### app/main.py
```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from shared_models import User, UserRole, Status
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
    return user
```

## Django проект

### requirements.txt
```txt
django>=4.2.0
psycopg2-binary>=2.9.0
git+https://github.com/ViachaslauKazakou/shared-models.git
```

### settings.py
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Добавьте в INSTALLED_APPS если нужно
INSTALLED_APPS = [
    # ... ваши приложения
    'shared_models',
]
```

## Microservice архитектура

### docker-compose.yml
```yaml
version: '3.8'
services:
  user-service:
    build: ./user-service
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/users_db
    depends_on:
      - postgres
      
  forum-service:
    build: ./forum-service  
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/forum_db
    depends_on:
      - postgres
      
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
volumes:
  postgres_data:
```

### Dockerfile для сервиса
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Alembic конфигурация для сервиса

### alembic/env.py
```python
import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Импорт всех моделей
from shared_models.models import Base, User, Topic, Message

# Импорт локальных моделей сервиса (если есть)
# from myservice.models import MyModel

config = context.config
target_metadata = Base.metadata

def run_migrations_offline():
    url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = os.getenv("DATABASE_URL") or configuration["sqlalchemy.url"]
    
    connectable = engine_from_config(
        configuration,
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

## Тестирование

### conftest.py
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared_models import Base, User, UserRole, Status

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///test.db")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def test_user(db_session):
    user = User(
        username="testuser",
        email="test@example.com",
        user_type=UserRole.user,
        status=Status.active
    )
    db_session.add(user)
    db_session.commit()
    return user
```

### test_models.py
```python
from shared_models import User, Topic, UserRole, Status

def test_create_user(db_session):
    user = User(
        username="testuser",
        email="test@example.com", 
        user_type=UserRole.user,
        status=Status.active
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.username == "testuser"

def test_user_topics_relationship(db_session, test_user):
    topic = Topic(
        title="Test Topic",
        description="Test Description",
        user_id=test_user.id,
        is_active=True
    )
    db_session.add(topic)
    db_session.commit()
    
    assert len(test_user.topics) == 1
    assert test_user.topics[0].title == "Test Topic"
```
