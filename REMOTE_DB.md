# Работа с удаленной базой данных

## Описание

Для работы с удаленной базой данных AWS RDS созданы:

- Отдельный конфигурационный файл `alembic.remote.ini`
- Скрипт `scripts/deploy-remote-db.sh` для интерактивной работы
- Команды Makefile для прямого управления миграциями

## Конфигурационные файлы

### alembic.ini (локальная разработка)
```ini
# Локальная БД (по умолчанию)
sqlalchemy.url = postgresql+psycopg2://docker:docker@localhost:5433/postgres
```

### alembic.remote.ini (удаленная БД)
```ini
# Удаленная БД AWS RDS
sqlalchemy.url = postgresql+psycopg2://postgres:MySecurePassword123@learn-service-test-postgres.cil0uc6gcdkj.us-east-1.rds.amazonaws.com:5432/learnservice
```

## Использование

### Команды Makefile (рекомендуется)

```bash
# Интерактивный скрипт
make deploy-remote

# Проверить текущую миграцию
make remote-current

# Применить все миграции (с подтверждением)
make remote-upgrade

# Показать историю миграций
make remote-history

# Откатить миграцию (ОПАСНО!)
make remote-downgrade
```

### Прямые команды Alembic

```bash
# Текущая миграция
poetry run alembic -c alembic.remote.ini current

# Применить миграции
poetry run alembic -c alembic.remote.ini upgrade head

# История миграций
poetry run alembic -c alembic.remote.ini history

# Откат к конкретной ревизии
poetry run alembic -c alembic.remote.ini downgrade <revision>
```

### Интерактивный скрипт

```bash
./scripts/deploy-remote-db.sh
```

## Настройки подключения

Скрипт использует следующие параметры подключения к удаленной БД:

- **Хост**: `learn-service-test-postgres.cil0uc6gcdkj.us-east-1.rds.amazonaws.com`
- **Порт**: `5432`
- **Пользователь**: `postgres`
- **База данных**: `learnservice`
- **Пароль**: запрашивается при выполнении

## Переменные окружения

Для автоматизации можно установить пароль через переменную окружения:

```bash
export PGPASSWORD="your_password"
make deploy-remote
```

## Безопасность

⚠️ **ВНИМАНИЕ**: Работа с ПРОДАКШН базой данных!

### Правила безопасности:
- 🔐 Никогда не коммитьте пароли в git
- 📋 Всегда проверяйте состояние миграций перед применением  
- 💾 Делайте резервные копии перед важными изменениями
- ✅ Тестируйте миграции на локальной БД
- 🚫 Команды с подтверждением (особенно downgrade)

### Конфигурация переменных окружения

Создайте файл `.env.remote` на основе `.env.remote.example`:

```bash
cp .env.remote.example .env.remote
# Отредактируйте .env.remote с правильными значениями
```

Файл `.env.remote` автоматически исключен из git.

## Возможности скрипта

1. **Проверка подключения** - тестирует доступность удаленной БД
2. **Состояние миграций** - показывает текущую версию и доступные миграции
3. **Применение миграций** - применяет все новые миграции к удаленной БД
4. **Просмотр таблиц** - показывает список всех таблиц в БД
5. **Полный цикл** - выполняет все операции последовательно

## Требования

- Poetry (для активации виртуального окружения)
- psql (PostgreSQL client)
- Доступ к удаленной БД
- Файл `alembic.ini` в корне проекта

## Принцип работы

Скрипт:
1. Активирует Poetry окружение
2. Создает временную копию `alembic.ini`
3. Заменяет строку подключения на удаленную БД
4. Выполняет команды Alembic
5. Очищает временные файлы

## Отличия от локальной разработки

- Не затрагивает локальные настройки
- Использует отдельную конфигурацию подключения
- Требует подтверждения для критических операций
- Работает только с указанной удаленной БД


```
PGPASSWORD=MySecurePassword123 psql -h learn-service-test-postgres.cil0uc6gcdkj.us-east-1.rds.amazonaws.com -p 5432 -U postgres -d learnservice
```