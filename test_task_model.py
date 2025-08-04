#!/usr/bin/env python3
"""
Тест модели Task в новом стиле SQLAlchemy 2.0
"""

import sys
import os
import uuid
from datetime import datetime

# Добавляем путь к shared_models в sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from shared_models import Task, SessionLocal

def test_task_model():
    print("🧪 Тестирование модели Task")
    print("=" * 40)
    
    with SessionLocal() as db:
        # Создаем задачу
        task = Task(
            task_id=str(uuid.uuid4()),
            user_id=1,  # Просто ID, без FK
            topic_id=1,  # Просто ID, без FK
            reply_to=None,
            context="Контекст для генерации ответа",
            question="Как работает SQLAlchemy 2.0?",
            status="pending"
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        print(f"✅ Создана задача: {task.question[:50]}...")
        print(f"   ID: {task.id}")
        print(f"   Task ID: {task.task_id}")
        print(f"   Статус: {task.status}")
        print(f"   User ID: {task.user_id}")
        print(f"   Topic ID: {task.topic_id}")
        print(f"   Попытки: {task.attempts}/{task.max_attempts}")
        print(f"   Создано: {task.created_at}")
        
        # Обновляем статус
        task.status = "processing"
        task.started_at = datetime.now()
        task.attempts += 1
        db.commit()
        
        print(f"✅ Статус обновлен: {task.status}")
        print(f"   Попытки: {task.attempts}")
        print(f"   Начато: {task.started_at}")
        
        # Завершаем задачу
        task.status = "completed"
        task.result = "Ответ от ИИ: SQLAlchemy 2.0 использует новый синтаксис..."
        task.completed_at = datetime.now()
        db.commit()
        
        print(f"✅ Задача завершена: {task.status}")
        print(f"   Результат: {task.result[:50]}...")
        print(f"   Завершено: {task.completed_at}")
        
        # Создаем задачу с ошибкой
        error_task = Task(
            task_id=str(uuid.uuid4()),
            user_id=2,
            question="Некорректный запрос",
            status="failed",
            error_message="Ошибка обработки запроса",
            attempts=3,
            max_attempts=3
        )
        
        db.add(error_task)
        db.commit()
        db.refresh(error_task)
        
        print(f"✅ Создана задача с ошибкой: {error_task.question}")
        print(f"   Статус: {error_task.status}")
        print(f"   Ошибка: {error_task.error_message}")
        
        # Проверяем запрос задач
        all_tasks = db.query(Task).all()
        print(f"\n📊 Всего задач в базе: {len(all_tasks)}")
        
        pending_tasks = db.query(Task).filter(Task.status == "pending").count()
        completed_tasks = db.query(Task).filter(Task.status == "completed").count()
        failed_tasks = db.query(Task).filter(Task.status == "failed").count()
        
        print(f"   Ожидающих: {pending_tasks}")
        print(f"   Завершенных: {completed_tasks}")
        print(f"   Неудачных: {failed_tasks}")
        
        # Откатываем изменения
        db.rollback()
        
        print("\n🎉 Все тесты прошли успешно!")

if __name__ == "__main__":
    test_task_model()
