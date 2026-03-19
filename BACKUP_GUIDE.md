# Резервное копирование и восстановление удаленной БД

Скрипт `scripts/backup-remote-db.sh` предоставляет полный набор инструментов для резервного копирования и восстановления удаленной PostgreSQL БД на AWS RDS.

## Быстрый старт

### 1. Настройка переменных окружения (опционально)

Создайте файл `.env.backup` скопировав пример:

```bash
cp .env.backup.example .env.backup
```

Отредактируйте `.env.backup` с вашими реальными параметрами:

```env
SOURCE_DB_HOST=your-source-db.rds.amazonaws.com
SOURCE_DB_PASSWORD=your-password
TARGET_DB_HOST=your-target-db.rds.amazonaws.com
TARGET_DB_PASSWORD=target-password
```

Затем скрипт будет автоматически загружать эти переменные при запуске.

### 2. Создать бэкап

```bash
make backup-remote
# или напрямую
./scripts/backup-remote-db.sh
```

Выберите пункт **1** для создания сжатого бэкапа (рекомендуется) или **2** для текстового SQL дампа.

### 3. Посмотреть созданные бэкапы

```bash
make backup-list
```

### 4. Восстановить БД на новом инстансе

```bash
make backup-remote
```

Выберите пункт **3** и следуйте инструкциям. Скрипт запросит параметры целевого хоста.

## Переменные окружения

### Способ 1: Через .env.backup файл (рекомендуется)

Создайте и отредактируйте файл `.env.backup`:

```bash
cp .env.backup.example .env.backup
# отредактируйте параметры
nano .env.backup
```

Скрипт автоматически загружает этот файл при запуске. Содержимое:

```env
SOURCE_DB_HOST="simple-ec2-db.cecurbs9fk6o.us-east-1.rds.amazonaws.com"
SOURCE_DB_PORT="5432"
SOURCE_DB_USER="postgres"
SOURCE_DB_NAME="learnservicedatabase"
SOURCE_DB_PASSWORD="vk-db-postgres"

TARGET_DB_HOST="new-db.region.rds.amazonaws.com"
TARGET_DB_PORT="5432"
TARGET_DB_USER="postgres"
TARGET_DB_NAME="learnservicedatabase"
TARGET_DB_PASSWORD="password"
```

**Важно**: `.env.backup` добавлен в `.gitignore`, так что ваши пароли не будут закоммичены в репозиторий.

Затем просто используйте:

```bash
make backup-remote
```

### Способ 2: Через переменные окружения (для CI/CD)

Переопределите параметры через export:

```bash
export SOURCE_DB_PASSWORD="new-password"
./scripts/backup-remote-db.sh
```

### Способ 3: Интерактивный ввод

Если переменные не установлены, скрипт будет запрашивать параметры в интерактивном режиме при восстановлении.

## Функции скрипта

| Пункт | Описание |
|-------|---------|
| **1** | Создать бэкап в custom формате (`.dump`) — сжатый, рекомендуется для больших БД |
| **2** | Создать SQL дамп (`.sql`) — текстовый формат, можно редактировать перед восстановлением |
| **3** | Восстановить БД из бэкапа на новом инстансе |
| **4** | Показать список созданных бэкапов и их размер |
| **5** | Проверить целостность бэкапа (только для custom формата) |
| **6** | Удалить старый бэкап |
| **7** | Выход |

## Примеры использования

### Пример 1: С файлом .env.backup (рекомендуется)

```bash
# Шаг 1: Создаем .env.backup с параметрами
cp .env.backup.example .env.backup
nano .env.backup  # Отредактируйте параметры

# Шаг 2: Создать бэкап
make backup-remote
# Выбираем: 1 (Create backup)

# Шаг 3: Проверить список бэкапов
make backup-list

# Шаг 4: Проверить целостность (опционально)
make backup-remote
# Выбираем: 5 (Verify backup)
```

### Пример 2: Полный цикл резервного копирования

```bash
# Подготовка
cp .env.backup.example .env.backup
# Отредактируйте SOURCE_DB_* параметры в .env.backup

# Создать бэкап исходной БД
make backup-remote
# Выбираем: 1

# Проверить список бэкапов
make backup-list

# Проверить целостность (опционально)
make backup-remote
# Выбираем: 5
```

### Пример 3: Восстановление на новом хосте

```bash
# Подготовка
cp .env.backup.example .env.backup
# Отредактируйте ТОЛЬКО SOURCE_DB_* параметры для чтения последнего бэкапа
# TARGET_DB_* будет запрошен при восстановлении

# Открываем утилиту восстановления
make backup-remote
# Выбираем: 3 (Restore from backup)

# Выбираем нужный бэкап из списка

# Вводим параметры нового хоста
# Host: new-db.eu-west-1.rds.amazonaws.com
# Port: 5432
# User: postgres
# Database: learnservicedatabase
# Password: (вводим пароль от нового инстанса)

# Подтверждаем восстановление (yes/no)
```

### Пример 4: Скрипт для полной миграции (Shell)

```bash
#!/bin/bash

# 1. Создать .env.backup с параметрами
cat > .env.backup << 'EOF'
SOURCE_DB_HOST=old-db.us-east-1.rds.amazonaws.com
SOURCE_DB_PASSWORD=old-password
TARGET_DB_HOST=new-db.eu-west-1.rds.amazonaws.com
TARGET_DB_PASSWORD=new-password
EOF

# 2. Создать бэкап (выбор опции 1)
echo "1" | make backup-remote

# 3. Подождать завершения
sleep 30

# 4. Восстановить (выбор опции 3)
echo "3" | make backup-remote
EOF
```

### Пример 5: Использование через export (для CI/CD без файла)

```bash
export SOURCE_DB_HOST="old.rds.amazonaws.com"
export SOURCE_DB_PASSWORD="password"
export TARGET_DB_HOST="new.rds.amazonaws.com"
export TARGET_DB_PASSWORD="password"
make backup-remote
```

## Структура директорий

```
project-root/
├── scripts/
│   └── backup-remote-db.sh        # Основной скрипт (400+ строк)
│
├── backups/                        # Автоматически создается
│   ├── backup_20260316_143022.dump
│   ├── backup_20260316_120530.dump
│   └── backup_20260314_095421.sql
│
└── backups/.backup_manifest        # Контрольные суммы бэкапов
```

## Форматы бэкапов

### Custom формат (`.dump`) — Рекомендуется

- **Размер**: Сжатый, обычно в 3-5 раз меньше, чем SQL
- **Скорость**: Быстрое восстановление
- **Гибкость**: Можно выбрать, какие таблицы и объекты восстанавливать
- **Использует**: `pg_dump -F c` и `pg_restore`

Пример:
```
-rw-r--r-- 1 user staff 45M Mar 16 14:30 backup_20260316_143022.dump
```

### SQL формат (`.sql`)

- **Размер**: Больший, текстовый формат
- **Скорость**: Медленнее при восстановлении
- **Гибкость**: Можно отредактировать SQL перед восстановлением
- **Использует**: `pg_dump` (стандартный) и `psql`

Пример:
```
-rw-r--r-- 1 user staff 180M Mar 16 12:05 backup_20260314_095421.sql
```

## Проверка целостности

Скрипт автоматически вычисляет MD5 контрольную сумму при создании бэкапа:

```
MD5: c3fcd3d76192e4007dfb496cca67e13b
```

Функция **5** позволяет проверить, что файл не повредился:

```bash
make backup-remote
# Выбираем: 5
# Выбираем бэкап для проверки
# ✅ Бэкап в порядке
```

## Советы и трюки

### Автоматическое резервное копирование (cron)

```bash
# Каждый день в 02:00 создавать бэкап
0 2 * * * cd /Users/Viachaslau_Kazakou/Work/shared-models && SOURCE_DB_PASSWORD="pass" /bin/bash -c 'echo "1" | ./scripts/backup-remote-db.sh'
```

### Загрузка бэкапа в облако (S3)

```bash
# После создания бэкапа отправить в AWS S3
make backup-remote
# Выбираем: 1

aws s3 cp backups/backup_*.dump s3://my-backup-bucket/
```

### Ограничение размера директории бэкапов

```bash
# Удерживать только последние 5 бэкапов
cd backups/
ls -t backup_* | tail -n +6 | xargs rm -f
```

## Безопасность

⚠️ **Важно**: Пароли не должны храниться в открытом виде в скриптах!

Рекомендуемый способ:

```bash
# Использовать ~/.pgpass для PostgreSQL
cat > ~/.pgpass << EOF
simple-ec2-db.cecurbs9fk6o.us-east-1.rds.amazonaws.com:5432:learnservicedatabase:postgres:vk-db-postgres
EOF

chmod 600 ~/.pgpass
```

Или использовать переменные окружения при запуске:

```bash
SOURCE_DB_PASSWORD="your-password" make backup-remote
```

## Решение проблем

### Ошибка: "pg_dump not found"

Установите PostgreSQL client:

```bash
# macOS
brew install postgresql

# Linux (Ubuntu/Debian)
sudo apt-get install postgresql-client

# Linux (RHEL/CentOS)
sudo yum install postgresql
```

### Ошибка: "Connection refused"

Проверьте:
1. Параметры хоста и порта
2. Доступность сервера из вашей сети
3. Security Groups в AWS (убедитесь, что порт 5432 открыт)
4. Пароль и имя пользователя

### Бэкап занимает слишком много места

- Используйте custom формат (`.dump`) вместо SQL
- Удаляйте старые бэкапы: `make backup-remote` → выбираем 6
- Загружайте бэкапы в облако (S3) и удаляйте локальные копии

## Дополнительно

- Полная документация по `pg_dump`: [PostgreSQL Docs](https://www.postgresql.org/docs/current/app-pgdump.html)
- Полная документация по `pg_restore`: [PostgreSQL Docs](https://www.postgresql.org/docs/current/app-pgrestore.html)
