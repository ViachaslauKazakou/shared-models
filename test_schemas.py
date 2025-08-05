#!/usr/bin/env python3
"""
Тест Pydantic схем для категорий и подкатегорий
"""

import sys
import os
from datetime import datetime

# Добавляем путь к shared_models в sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from shared_models import (
    CategoryCreate,
    CategoryResponse,
    SubcategoryCreate,
    SubcategoryResponse,
    TopicCreate,
    TopicWithCategories,
)


def test_schemas():
    print("🧪 Тестирование Pydantic схем")
    print("=" * 50)

    # Тест создания категории
    category_data = {
        "name": "Технологии",
        "description": "Обсуждение технологий",
        "slug": "tech",
        "color": "#007BFF",
        "icon": "laptop",
    }

    category_create = CategoryCreate(**category_data)
    print(f"✅ CategoryCreate: {category_create.name}")

    # Тест ответа категории
    category_response_data = {
        **category_data,
        "id": 1,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "is_active": True,
        "sort_order": 1,
    }

    category_response = CategoryResponse(**category_response_data)
    print(f"✅ CategoryResponse: {category_response.name} (ID: {category_response.id})")

    # Тест создания подкатегории
    subcategory_data = {
        "name": "Python",
        "description": "Вопросы по Python",
        "slug": "python",
        "color": "#3776AB",
        "icon": "python",
        "category_id": 1,
    }

    subcategory_create = SubcategoryCreate(**subcategory_data)
    print(f"✅ SubcategoryCreate: {subcategory_create.name}")

    # Тест ответа подкатегории
    subcategory_response_data = {
        **subcategory_data,
        "id": 1,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "is_active": True,
        "sort_order": 1,
    }

    subcategory_response = SubcategoryResponse(**subcategory_response_data)
    print(f"✅ SubcategoryResponse: {subcategory_response.name} (ID: {subcategory_response.id})")

    # Тест создания топика с категориями
    topic_data = {
        "title": "Как использовать SQLAlchemy?",
        "description": "Вопрос по ORM",
        "user_id": 1,
        "category_id": 1,
        "subcategory_id": 1,
    }

    topic_create = TopicCreate(**topic_data)
    print(f"✅ TopicCreate: {topic_create.title}")
    print(f"   Категория ID: {topic_create.category_id}")
    print(f"   Подкатегория ID: {topic_create.subcategory_id}")

    # Тест TopicWithCategories
    topic_with_categories_data = {
        **topic_data,
        "id": 1,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "is_active": True,
        "category": category_response,
        "subcategory": subcategory_response,
    }

    topic_with_categories = TopicWithCategories(**topic_with_categories_data)
    print(f"✅ TopicWithCategories: {topic_with_categories.title}")
    print(f"   Категория: {topic_with_categories.category.name if topic_with_categories.category else 'None'}")
    print(f"   Подкатегория: {topic_with_categories.subcategory.name if topic_with_categories.subcategory else 'None'}")

    # Тест TopicCreate без категорий
    topic_no_categories = TopicCreate(title="Общее обсуждение", description="Топик без категорий")
    print(f"✅ TopicCreate без категорий: {topic_no_categories.title}")
    print(f"   Категория ID: {topic_no_categories.category_id}")
    print(f"   Подкатегория ID: {topic_no_categories.subcategory_id}")

    print("\n🎉 Все схемы работают корректно!")


if __name__ == "__main__":
    test_schemas()
