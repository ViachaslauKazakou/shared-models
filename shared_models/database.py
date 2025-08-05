"""Database configuration and setup."""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Загружаем переменные из .env файла
load_dotenv()

# Получаем URL базы данных из переменной окружения или используем SQLite по умолчанию
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./shared_models.db")

# Настройки пула соединений
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

# Создаем движок базы данных с настройками пула
if DATABASE_URL.startswith("sqlite"):
    # Для SQLite используем упрощенные настройки
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}, echo=os.getenv("LOG_LEVEL") == "DEBUG"
    )
else:
    # Для PostgreSQL и других баз используем пул соединений
    engine = create_engine(
        DATABASE_URL,
        pool_size=DB_POOL_SIZE,
        max_overflow=DB_MAX_OVERFLOW,
        pool_timeout=DB_POOL_TIMEOUT,
        pool_recycle=DB_POOL_RECYCLE,
        echo=os.getenv("LOG_LEVEL") == "DEBUG",
    )

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базовый класс для моделей
Base = declarative_base()


def get_db():
    """Получить сессию базы данных."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
