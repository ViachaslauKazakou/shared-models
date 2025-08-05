#!/usr/bin/env python3
"""Тест импорта всех компонентов пакета."""


def test_imports():
    """Проверка, что все основные компоненты можно импортировать."""
    try:
        # Тест импорта моделей
        from shared_models import (
            User,
            Topic,
            Message,
            Embedding,
            MessageEmbedding,
            UserKnowledgeRecord,
            UserMessageExample,
            Base,
        )

        print("✅ Модели импортированы успешно")

        # Тест импорта схем
        from shared_models import UserRole, Status

        print("✅ Схемы импортированы успешно")

        # Тест импорта утилит для БД
        from shared_models import engine, SessionLocal, get_db

        print("✅ Утилиты БД импортированы успешно")

        # Проверка енумов
        assert hasattr(UserRole, "admin")
        assert hasattr(UserRole, "user")
        assert hasattr(Status, "active")
        assert hasattr(Status, "pending")
        print("✅ Енумы работают корректно")

        # Проверка базовых классов
        assert hasattr(User, "__tablename__")
        assert hasattr(Topic, "__tablename__")
        assert hasattr(Message, "__tablename__")
        print("✅ Модели SQLAlchemy настроены корректно")

        print("\n🎉 Все тесты импорта прошли успешно!")
        return True

    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False


def test_model_creation():
    """Тест создания экземпляров моделей."""
    try:
        from shared_models import User, Topic, Message, UserRole, Status

        # Создание пользователя
        user = User(username="test_user", email="test@example.com", user_type=UserRole.user, status=Status.active)
        assert user.username == "test_user"
        print("✅ Создание User работает")

        # Создание темы
        topic = Topic(title="Test Topic", description="Test Description", user_id=1, is_active=True)
        assert topic.title == "Test Topic"
        print("✅ Создание Topic работает")

        # Создание сообщения
        message = Message(content="Test Message", author_name="test_user", topic_id=1, user_id=1)
        assert message.content == "Test Message"
        print("✅ Создание Message работает")

        print("\n🎉 Все тесты создания моделей прошли успешно!")
        return True

    except Exception as e:
        print(f"❌ Ошибка создания моделей: {e}")
        return False


def main():
    """Основная функция тестирования."""
    print("🧪 Тестирование пакета shared-models...")
    print("=" * 50)

    success = True

    print("\n📦 Тест импорта компонентов:")
    success &= test_imports()

    print("\n🏗️ Тест создания моделей:")
    success &= test_model_creation()

    print("\n" + "=" * 50)
    if success:
        print("✅ Все тесты прошли успешно! Пакет готов к использованию.")
        exit(0)
    else:
        print("❌ Некоторые тесты не прошли!")
        exit(1)


if __name__ == "__main__":
    main()
