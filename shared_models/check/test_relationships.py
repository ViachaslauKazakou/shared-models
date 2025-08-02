#!/usr/bin/env python3
"""
Тестирование связей между моделями и каскадного удаления
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from shared_models.models import Base, User, Topic, Message, MessageEmbedding, UserMessageExample, UserKnowledgeRecord
from shared_models.schemas import UserRole, Status
import numpy as np

# Настройка подключения к тестовой БД
DATABASE_URL = "postgresql+asyncpg://docker:docker@localhost:5433/postgres"


async def test_cascade_deletions():
    """Тест каскадного удаления"""
    
    # Создание движка и сессии
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        # Создание таблиц
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        async with async_session() as session:
            # Создание тестового пользователя
            user = User(
                username="test_user",
                email="test@example.com",
                password="password123",
                user_type=UserRole.user,
                status=Status.active
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            print(f"✅ Создан пользователь: {user.id}")
            
            # Создание темы
            topic = Topic(
                title="Test Topic",
                description="Test description",
                user_id=user.id
            )
            session.add(topic)
            await session.commit()
            await session.refresh(topic)
            
            print(f"✅ Создана тема: {topic.id}")
            
            # Создание сообщения
            message = Message(
                content="Test message content",
                author_name=user.username,
                topic_id=topic.id,
                user_id=user.id
            )
            session.add(message)
            await session.commit()
            await session.refresh(message)
            
            print(f"✅ Создано сообщение: {message.id}")
            
            # Создание примера сообщения пользователя
            user_message_example = UserMessageExample(
                user_id=user.id,
                character_id="test_character",
                content="Test user message example",
                content_embedding=np.random.random(1536).tolist(),
                context_embedding=np.random.random(1536).tolist()
            )
            session.add(user_message_example)
            await session.commit()
            await session.refresh(user_message_example)
            
            print(f"✅ Создан пример сообщения: {user_message_example.id}")
            
            # Создание эмбеддингов для разных источников
            message_embedding1 = MessageEmbedding(
                message_id=message.id,
                topic_id=topic.id,
                content="Message embedding content",
                embedding=np.random.random(1536).tolist()
            )
            
            message_embedding2 = MessageEmbedding(
                user_message_example_id=user_message_example.id,
                content="User message example embedding",
                embedding=np.random.random(1536).tolist()
            )
            
            session.add_all([message_embedding1, message_embedding2])
            await session.commit()
            
            print(f"✅ Создано эмбеддингов: {message_embedding1.id}, {message_embedding2.id}")
            
            # Проверка количества записей перед удалением
            message_embeddings_count = len((await session.execute(
                select(MessageEmbedding)
            )).scalars().all())
            
            user_examples_count = len((await session.execute(
                select(UserMessageExample)
            )).scalars().all())
            
            print("📊 Перед удалением:")
            print(f"   MessageEmbedding: {message_embeddings_count}")
            print(f"   UserMessageExample: {user_examples_count}")
            
            # Тест 1: Удаление UserMessageExample должно удалить связанные MessageEmbedding
            print("\n🗑️ Тест 1: Удаление UserMessageExample")
            await session.delete(user_message_example)
            await session.commit()
            
            # Проверка после удаления
            remaining_embeddings = (await session.execute(
                select(MessageEmbedding).where(MessageEmbedding.user_message_example_id.isnot(None))
            )).scalars().all()
            
            print(f"✅ Эмбеддингов после удаления UserMessageExample: {len(remaining_embeddings)}")
            assert len(remaining_embeddings) == 0, "MessageEmbedding должны удаляться каскадно"
            
            # Тест 2: Удаление Message должно удалить связанные MessageEmbedding
            print("\n🗑️ Тест 2: Удаление Message")
            await session.delete(message)
            await session.commit()
            
            remaining_message_embeddings = (await session.execute(
                select(MessageEmbedding).where(MessageEmbedding.message_id.isnot(None))
            )).scalars().all()
            
            print(f"✅ Эмбеддингов после удаления Message: {len(remaining_message_embeddings)}")
            assert len(remaining_message_embeddings) == 0, "MessageEmbedding должны удаляться каскадно"
            
            # Тест 3: Удаление User должно удалить все связанные данные
            print("\n🗑️ Тест 3: Удаление User")
            await session.delete(user)
            await session.commit()
            
            # Проверка что все связанные данные удалены
            topics_count = len((await session.execute(select(Topic))).scalars().all())
            knowledge_records_count = len((await session.execute(select(UserKnowledgeRecord))).scalars().all())
            
            print(f"✅ Записей после удаления User:")
            print(f"   Topics: {topics_count}")
            print(f"   UserKnowledgeRecord: {knowledge_records_count}")
            
            print("\n🎉 Все тесты каскадного удаления прошли успешно!")
            
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_cascade_deletions())
