# Категории и подкатегории для топиков

## Выполненные изменения

### 1. Модели базы данных (`models.py`)

Добавлены новые модели:

#### Category (Категория)
- `id` - уникальный идентификатор 
- `name` - название категории
- `description` - описание (опционально)
- `slug` - человекочитаемый URL
- `color` - цвет для UI (опционально)
- `icon` - иконка (опционально) 
- `is_active` - активна ли категория
- `sort_order` - порядок сортировки
- `created_at` / `updated_at` - временные метки

#### Subcategory (Подкатегория)
- Те же поля что и у Category
- `category_id` - связь с родительской категорией

#### Обновления Topic
- `category_id` - опциональная связь с категорией
- `subcategory_id` - опциональная связь с подкатегорией

### 2. Pydantic схемы (`schemas.py`)

Добавлены схемы для работы с API:

#### Категории
- `CategoryBase` - базовые поля
- `CategoryCreate` - создание категории  
- `CategoryUpdate` - обновление категории
- `CategoryResponse` - ответ API с полной информацией

#### Подкатегории
- `SubcategoryBase` - базовые поля
- `SubcategoryCreate` - создание подкатегории
- `SubcategoryUpdate` - обновление подкатегории  
- `SubcategoryResponse` - ответ API с полной информацией

#### Обновления топиков
- `TopicCreate` - теперь принимает `category_id` и `subcategory_id`
- `TopicUpdate` - поддержка обновления категорий
- `TopicResponse` - включает ID категорий
- `TopicWithCategories` - новая схема с полной информацией о категориях
- `TopicList` - обновлена для включения категорий

### 3. Миграция базы данных

Создана миграция `2025_08_04_1223-3ca9d72fe2ba_add_categories_and_subcategories_for_.py`:

- Создание таблицы `categories`
- Создание таблицы `subcategories` 
- Добавление полей `category_id` и `subcategory_id` в таблицу `topics`
- Создание внешних ключей и индексов

### 4. Обновления экспортов (`__init__.py`)

Добавлены экспорты всех новых моделей и схем для удобного импорта.

## Использование

### Создание категории и подкатегории

```python
from shared_models import Category, Subcategory, SessionLocal

with SessionLocal() as db:
    # Создаем категорию
    category = Category(
        name="Технологии",
        description="Обсуждение технологий и программирования",
        slug="tech",
        color="#007BFF",
        icon="laptop",
        sort_order=1
    )
    db.add(category)
    db.commit()
    
    # Создаем подкатегорию
    subcategory = Subcategory(
        name="Python",
        description="Вопросы по языку программирования Python",
        slug="python",
        color="#3776AB", 
        icon="python",
        category_id=category.id,
        sort_order=1
    )
    db.add(subcategory)
    db.commit()
```

### Создание топика с категориями

```python
from shared_models import Topic, SessionLocal

with SessionLocal() as db:
    topic = Topic(
        title="Как использовать SQLAlchemy с pgvector?",
        description="Обсуждение интеграции SQLAlchemy с расширением pgvector",
        user_id=1,
        category_id=1,      # Опционально
        subcategory_id=1    # Опционально
    )
    db.add(topic)
    db.commit()
```

### Создание топика без категорий

```python
# Топики могут существовать без категорий
topic = Topic(
    title="Общее обсуждение",
    description="Топик без привязки к категориям",
    user_id=1
    # category_id и subcategory_id остаются None
)
```

## Тестирование

Созданы тесты:

- `test_categories.py` - тестирование моделей и связей в базе данных
- `test_schemas.py` - тестирование Pydantic схем

Все тесты проходят успешно ✅

## Структура категорий

```
Категория (например: "Технологии")
├── Подкатегория 1 (например: "Python")
│   ├── Топик 1
│   └── Топик 2
├── Подкатегория 2 (например: "JavaScript")
│   ├── Топик 3
│   └── Топик 4
└── Топики без подкатегории (привязанные только к категории)

Топики без категорий (category_id = None, subcategory_id = None)
```

## Следующие шаги

1. ✅ Модели созданы
2. ✅ Схемы добавлены  
3. ✅ Миграция применена
4. ✅ Тесты пройдены
5. 🔄 Можно добавить API endpoints для работы с категориями
6. 🔄 Можно добавить админку для управления категориями
7. 🔄 Можно добавить фильтрацию топиков по категориям
