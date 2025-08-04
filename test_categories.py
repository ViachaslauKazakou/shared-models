#!/usr/bin/env python3
"""Скрипт для тестирования новых моделей категорий и подкатегорий."""

from shared_models.database import SessionLocal
from shared_models.models import User, Topic, Category, Subcategory
from shared_models.schemas import UserRole, Status

def test_categories_and_subcategories():
    """Тестирование создания категорий, подкатегорий и топиков с ними."""
    db = SessionLocal()
    
    try:
        # Создаем тестового пользователя
        test_user = User(
            username="test_categories_user",
            firstname="Test",
            lastname="User",
            password="hashed_password",
            email="test_categories@example.com",
            user_type=UserRole.user,
            status=Status.active
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✅ Создан пользователь: {test_user.username} (ID: {test_user.id})")
        
        # Создаем категорию
        tech_category = Category(
            name="Технологии",
            description="Обсуждение технологий и программирования",
            slug="tech",
            color="#007BFF",
            icon="laptop",
            sort_order=1
        )
        db.add(tech_category)
        db.commit()
        db.refresh(tech_category)
        print(f"✅ Создана категория: {tech_category.name} (ID: {tech_category.id})")
        
        # Создаем подкатегорию
        python_subcategory = Subcategory(
            name="Python",
            description="Вопросы по языку программирования Python",
            slug="python",
            color="#3776AB",
            icon="python",
            category_id=tech_category.id,
            sort_order=1
        )
        db.add(python_subcategory)
        db.commit()
        db.refresh(python_subcategory)
        print(f"✅ Создана подкатегория: {python_subcategory.name} (ID: {python_subcategory.id})")
        
        # Создаем топик с категорией и подкатегорией
        test_topic = Topic(
            title="Как использовать SQLAlchemy с pgvector?",
            description="Обсуждение интеграции SQLAlchemy с расширением pgvector",
            user_id=test_user.id,
            category_id=tech_category.id,
            subcategory_id=python_subcategory.id
        )
        db.add(test_topic)
        db.commit()
        db.refresh(test_topic)
        print(f"✅ Создан топик: {test_topic.title} (ID: {test_topic.id})")
        
        # Проверяем связи
        print("\n📊 Проверка связей:")
        
        # Категория -> Подкатегории
        category_with_subcategories = db.query(Category).filter(Category.id == tech_category.id).first()
        print(f"   Категория '{category_with_subcategories.name}' имеет {len(category_with_subcategories.subcategories)} подкатегорий")
        for sub in category_with_subcategories.subcategories:
            print(f"     - {sub.name}")
        
        # Категория -> Топики
        print(f"   Категория '{category_with_subcategories.name}' имеет {len(category_with_subcategories.topics)} топиков")
        for topic in category_with_subcategories.topics:
            print(f"     - {topic.title}")
        
        # Подкатегория -> Топики
        subcategory_with_topics = db.query(Subcategory).filter(Subcategory.id == python_subcategory.id).first()
        print(f"   Подкатегория '{subcategory_with_topics.name}' имеет {len(subcategory_with_topics.topics)} топиков")
        for topic in subcategory_with_topics.topics:
            print(f"     - {topic.title}")
        
        # Топик -> Категория и подкатегория
        topic_with_relations = db.query(Topic).filter(Topic.id == test_topic.id).first()
        print(f"   Топик '{topic_with_relations.title}':")
        print(f"     Категория: {topic_with_relations.category.name if topic_with_relations.category else 'Нет'}")
        print(f"     Подкатегория: {topic_with_relations.subcategory.name if topic_with_relations.subcategory else 'Нет'}")
        
        print("\n✅ Все тесты пройдены успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def test_topic_without_categories():
    """Тестирование создания топика без категорий (опциональные поля)."""
    db = SessionLocal()
    
    try:
        # Получаем существующего пользователя
        user = db.query(User).filter(User.username == "test_categories_user").first()
        if not user:
            print("❌ Пользователь не найден")
            return False
        
        # Создаем топик без категорий
        simple_topic = Topic(
            title="Общее обсуждение",
            description="Топик без привязки к категориям",
            user_id=user.id
            # category_id и subcategory_id не указываем (они Optional)
        )
        db.add(simple_topic)
        db.commit()
        db.refresh(simple_topic)
        
        print(f"✅ Создан топик без категорий: {simple_topic.title}")
        print(f"   Категория: {simple_topic.category}")
        print(f"   Подкатегория: {simple_topic.subcategory}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании топика без категорий: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Основная функция."""
    print("🚀 Тестирование категорий и подкатегорий")
    print("=" * 50)
    
    # Тест 1: Полная цепочка с категориями
    if test_categories_and_subcategories():
        print("\n" + "=" * 50)
        
        # Тест 2: Топик без категорий
        test_topic_without_categories()
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    main()
