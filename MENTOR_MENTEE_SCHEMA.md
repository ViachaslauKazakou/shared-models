# Mentor-Mentee System: Database Schema Proposal

## Обзор

Этот документ описывает предложенные изменения в shared_models для реализации системы связей mentor-mentee.

## Новая таблица: MentorMentee

### Описание
Таблица для хранения связей между менторами и учениками. Позволяет:
- Ментору добавлять учеников в список для быстрого доступа к их прогрессу
- Ученику подписываться на обновления от ментора (новые тесты, курсы)
- Отслеживать статистику по занятиям между ментором и учеником

### SQL Schema

```python
class MentorMenteeStatus(str, enum.Enum):
    """Статус связи mentor-mentee"""
    PENDING = "pending"      # Отправлен запрос, ожидает подтверждения
    ACTIVE = "active"        # Активная связь
    PAUSED = "paused"        # Приостановлена
    COMPLETED = "completed"  # Завершена
    REJECTED = "rejected"    # Отклонена


class MentorMentee(Base):
    """Связь между ментором и учеником"""
    
    __tablename__ = "mentor_mentee"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Связи с пользователями
    mentor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    mentee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    # Статус связи
    status: Mapped[MentorMenteeStatus] = mapped_column(
        Enum(MentorMenteeStatus, name="mentor_mentee_status", native_enum=False),
        default=MentorMenteeStatus.PENDING,
        nullable=False
    )
    
    # Настройки подписки
    subscribe_to_quizzes: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    subscribe_to_courses: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    subscribe_to_subjects: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Заметки и описание
    mentor_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Заметки ментора об ученике")
    mentee_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Заметки ученика о менторе")
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    accepted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True,
        comment="Когда связь была принята"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True,
        comment="Когда связь была завершена"
    )
    
    # Кто инициировал связь
    initiated_by: Mapped[str] = mapped_column(
        String(10), 
        nullable=False,
        comment="'mentor' или 'mentee' - кто создал запрос"
    )
    
    # Relationships
    mentor: Mapped["User"] = relationship("User", foreign_keys=[mentor_id], backref="mentees")
    mentee: Mapped["User"] = relationship("User", foreign_keys=[mentee_id], backref="mentors")
    
    # Уникальность: один ментор - один ученик (одна активная связь)
    __table_args__ = (
        UniqueConstraint('mentor_id', 'mentee_id', name='unique_mentor_mentee_pair'),
        Index('idx_mentor_id_status', 'mentor_id', 'status'),
        Index('idx_mentee_id_status', 'mentee_id', 'status'),
    )
```

## Статистика по связям: Представление (View) или вычисляемые поля

Для получения статистики по занятиям между ментором и учеником можно использовать:

### Вариант 1: SQL View (рекомендуется для производительности)

```sql
CREATE VIEW mentor_mentee_statistics AS
SELECT 
    mm.id as relationship_id,
    mm.mentor_id,
    mm.mentee_id,
    mm.status,
    COUNT(ss.id) as total_bookings,
    SUM(CASE WHEN ss.status = 'completed' THEN 1 ELSE 0 END) as completed_sessions,
    SUM(CASE WHEN ss.status = 'confirmed' THEN 1 ELSE 0 END) as confirmed_sessions,
    SUM(CASE WHEN ss.status = 'pending' THEN 1 ELSE 0 END) as pending_sessions,
    MAX(ss.booked_date) as last_session_date,
    MIN(ss.booked_date) as first_session_date
FROM mentor_mentee mm
LEFT JOIN subject_schedule ss ON (
    ss.user_id = mm.mentee_id 
    AND ss.subject_id IN (
        SELECT id FROM subjects WHERE user_id = mm.mentor_id
    )
)
GROUP BY mm.id, mm.mentor_id, mm.mentee_id, mm.status;
```

### Вариант 2: Метод в application layer (более гибкий)

```python
class MentorMentee(Base):
    # ... поля выше ...
    
    async def get_session_statistics(self, session: AsyncSession) -> dict:
        """
        Получить статистику занятий между ментором и учеником
        
        Returns:
            dict с ключами:
            - total_bookings: общее количество бронирований
            - completed_sessions: завершенные занятия
            - confirmed_sessions: подтвержденные занятия
            - pending_sessions: ожидающие подтверждения
            - cancelled_sessions: отмененные занятия
            - last_session_date: дата последнего занятия
            - upcoming_sessions: список будущих занятий
        """
        pass  # Реализация в application код
```

## Изменения в существующих таблицах

### User (изменения не требуются)
- Связи добавляются через backref в MentorMentee
- `mentees` - список учеников (для mentor)
- `mentors` - список менторов (для mentee)

### UserProfile (опционально, для расширенного профиля)

```python
class UserProfile(Base):
    # ... существующие поля ...
    
    # Новые поля для ментора
    mentor_bio: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True,
        comment="Биография ментора, его специализация"
    )
    mentor_rate: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Почасовая ставка ментора"
    )
    mentor_available: Mapped[bool] = mapped_column(
        Boolean, 
        default=True,
        comment="Доступен ли ментор для новых учеников"
    )
    max_mentees: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Максимальное количество учеников"
    )
    
    # Новые поля для ученика
    learning_goals: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Цели обучения ученика"
    )
    preferred_learning_style: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Предпочитаемый стиль обучения"
    )
```

## Индексы для оптимизации

```sql
-- Быстрый поиск учеников ментора
CREATE INDEX idx_mentor_mentee_mentor_status ON mentor_mentee(mentor_id, status);

-- Быстрый поиск менторов ученика
CREATE INDEX idx_mentor_mentee_mentee_status ON mentor_mentee(mentee_id, status);

-- Поиск по датам
CREATE INDEX idx_mentor_mentee_created ON mentor_mentee(created_at);

-- Составной индекс для статистики
CREATE INDEX idx_mentor_mentee_composite ON mentor_mentee(mentor_id, mentee_id, status);
```

## Миграция данных

### Шаг 1: Создать таблицу
```bash
# Создать новую миграцию Alembic
alembic revision -m "add_mentor_mentee_table"
```

### Шаг 2: Заполнить существующие связи
Если есть существующие связи через SubjectSchedule, можно автоматически создать MentorMentee записи:

```python
# В миграции или скрипте
async def migrate_existing_relationships(session: AsyncSession):
    """
    Создать MentorMentee записи на основе существующих SubjectSchedule
    """
    query = select(
        Subject.user_id.label('mentor_id'),
        SubjectSchedule.user_id.label('mentee_id')
    ).join(
        SubjectSchedule, Subject.id == SubjectSchedule.subject_id
    ).where(
        SubjectSchedule.status != SubjectBookStatus.cancelled
    ).distinct()
    
    result = await session.execute(query)
    pairs = result.all()
    
    for mentor_id, mentee_id in pairs:
        # Проверить, существует ли уже связь
        existing = await session.execute(
            select(MentorMentee).where(
                MentorMentee.mentor_id == mentor_id,
                MentorMentee.mentee_id == mentee_id
            )
        )
        if not existing.scalar_one_or_none():
            relationship = MentorMentee(
                mentor_id=mentor_id,
                mentee_id=mentee_id,
                status=MentorMenteeStatus.ACTIVE,
                initiated_by='system',  # Автоматически созданная
                subscribe_to_quizzes=True,
                subscribe_to_courses=True
            )
            session.add(relationship)
    
    await session.commit()
```

## API Endpoints (для справки)

Следующие endpoints будут реализованы в learn-service:

```
POST   /{lang}/users/mentor/add-mentee        # Ментор добавляет ученика
POST   /{lang}/users/mentee/add-mentor        # Ученик подписывается на ментора
PUT    /{lang}/users/mentor-mentee/{id}       # Обновить связь (статус, настройки)
DELETE /{lang}/users/mentor-mentee/{id}       # Удалить связь
GET    /{lang}/users/mentor/mentees            # Список учеников ментора
GET    /{lang}/users/mentee/mentors            # Список менторов ученика
GET    /{lang}/users/mentor-mentee/{id}/stats # Статистика по связи
```

## Преимущества предложенного решения

1. **Явная связь**: Отдельная таблица для управления отношениями mentor-mentee
2. **Гибкие подписки**: Ученик может выбирать, на что подписываться (квизы, курсы, предметы)
3. **Статусы**: Полный жизненный цикл связи (pending → active → completed)
4. **Audit trail**: Временные метки для всех изменений статуса
5. **Двунаправленная инициация**: Запрос может создать как ментор, так и ученик
6. **Заметки**: Обе стороны могут делать заметки
7. **Производительность**: Индексы оптимизированы для частых запросов
8. **Масштабируемость**: Легко добавить новые поля (рейтинги, теги, и т.д.)

## Следующие шаги

1. ✅ Согласовать схему таблицы
2. ✅ Создать миграцию в shared_models репозитории
3. ✅ Реализовать модели MentorMentee и обновить UserProfile
4. ⏳ Реализовать manager в learn-service
5. ⏳ Создать API endpoints
6. ⏳ Обновить UI (профили ментора и ученика)
7. ⏳ Добавить тесты

---

**Дата создания**: 2026-03-01  
**Версия**: 1.0  
**Статус**: Proposal for Review
