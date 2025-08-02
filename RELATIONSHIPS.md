# Структура связей в shared-models

## Диаграмма связей

```
User (users)
├── topics (1:N, cascade delete)
├── messages (1:N)
├── knowledge_record (1:1, cascade delete)
└── message_examples (1:N, cascade delete)
    └── embeddings (1:N, cascade delete) ← MessageEmbedding

Topic (topics)
├── messages (1:N, cascade delete)
└── embeddings (1:N, cascade delete) ← MessageEmbedding

Message (messages)
├── replies (1:N, self-ref, cascade delete)
└── embeddings (1:N, cascade delete) ← MessageEmbedding

MessageEmbedding (message_embeddings)
├── message (N:1, optional)
├── topic (N:1, optional)
└── user_message_example (N:1, optional)

Embedding (embeddings)
└── (независимая таблица)

UserKnowledgeRecord (user_knowledge)
└── user (1:1)

UserMessageExample (user_message_examples)
├── user (N:1)
└── embeddings (1:N, cascade delete) ← MessageEmbedding
```

## Каскадные удаления

### ✅ При удалении User:
- Удаляются все связанные Topics
- Удаляются все связанные Messages 
- Удаляется UserKnowledgeRecord
- Удаляются все UserMessageExample
- Удаляются все MessageEmbedding через Topics, Messages и UserMessageExample

### ✅ При удалении Topic:
- Удаляются все связанные Messages
- Удаляются все связанные MessageEmbedding

### ✅ При удалении Message:
- Удаляются все дочерние Messages (replies)
- Удаляются все связанные MessageEmbedding

### ✅ При удалении UserMessageExample:
- Удаляются все связанные MessageEmbedding

## Особенности MessageEmbedding

`MessageEmbedding` - универсальная таблица для хранения эмбеддингов из разных источников:

- **message_id** - эмбеддинги обычных сообщений форума
- **topic_id** - эмбеддинги тем (дополнительная связь)
- **user_message_example_id** - эмбеддинги примеров сообщений пользователей

Все поля nullable, что позволяет гибко использовать таблицу для разных типов эмбеддингов.

## Тестирование

Для проверки связей запустите:

```bash
poetry run python test_relationships.py
```

Этот тест проверяет корректность каскадных удалений и целостность связей между таблицами.
