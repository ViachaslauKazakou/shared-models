#!/usr/bin/env python3
"""Скрипт для проверки подключения к базе данных и создания тестовых данных."""

import sys
import os
from datetime import datetime
import sqlalchemy as sa

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shared_models.database import engine, SessionLocal
from shared_models.models import User, Topic, Message
from shared_models.schemas import UserRole, Status


def check_connection():
    """Проверка подключения к базе данных."""
    try:
        with engine.connect() as connection:
            result = connection.execute(sa.text("SELECT 1 as test"))
            print("✅ Подключение к базе данных успешно!")
            print(f"📊 Результат тестового запроса: {result.fetchone()}")
            return True
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return False


def create_test_data():
    """Создание тестовых данных."""
    db = SessionLocal()
    try:
        # Создаем тестового пользователя
        test_user = User(
            username="test_user",
            firstname="Тест",
            lastname="Пользователь",
            password="hashed_password_here",
            email="test@example.com",
            user_type=UserRole.user,
            status=Status.active
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"✅ Создан тестовый пользователь: {test_user.username} (ID: {test_user.id})")
        
        # Создаем тестовую тему
        test_topic = Topic(
            title="Тестовая тема",
            description="Это тестовая тема для проверки работы базы данных",
            user_id=test_user.id,
            is_active=True
        )
        db.add(test_topic)
        db.commit()
        db.refresh(test_topic)
        
        print(f"✅ Создана тестовая тема: {test_topic.title} (ID: {test_topic.id})")
        
        # Создаем тестовое сообщение
        test_message = Message(
            content="Это тестовое сообщение для проверки работы базы данных",
            author_name=test_user.username,
            topic_id=test_topic.id,
            user_id=test_user.id
        )
        db.add(test_message)
        db.commit()
        db.refresh(test_message)
        
        print(f"✅ Создано тестовое сообщение (ID: {test_message.id})")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания тестовых данных: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def check_data():
    """Проверка созданных данных."""
    db = SessionLocal()
    try:
        users_count = db.query(User).count()
        topics_count = db.query(Topic).count()
        messages_count = db.query(Message).count()
        
        print(f"📊 Статистика базы данных:")
        print(f"   Пользователи: {users_count}")
        print(f"   Темы: {topics_count}")
        print(f"   Сообщения: {messages_count}")
        
        # Показываем последнего пользователя
        if users_count > 0:
            last_user = db.query(User).order_by(User.id.desc()).first()
            if last_user:
                print(f"   Последний пользователь: {last_user.username} ({last_user.email})")
            
    except Exception as e:
        print(f"❌ Ошибка проверки данных: {e}")
    finally:
        db.close()


def main():
    """Основная функция."""
    print("🚀 Проверка подключения к базе данных...")
    print("=" * 50)
    
    if not check_connection():
        print("❌ Не удалось подключиться к базе данных!")
        return
    
    print("\n📝 Создание тестовых данных...")
    print("=" * 50)
    
    if create_test_data():
        print("\n📊 Проверка созданных данных...")
        print("=" * 50)
        check_data()
        print("\n✅ Все проверки пройдены успешно!")
    else:
        print("\n❌ Ошибка при создании тестовых данных!")


if __name__ == "__main__":
    main()
