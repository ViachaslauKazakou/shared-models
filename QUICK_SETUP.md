# Быстрая настройка резервного копирования БД

## Один шаг - скопировать файл конфигурации

```bash
cp .env.backup.example .env.backup
```

## Два шага - отредактировать параметры

Откройте `.env.backup` в редакторе и обновите параметры подключения:

```bash
nano .env.backup
# или в VS Code:
code .env.backup
```

Пример содержимого:
```env
SOURCE_DB_HOST=simple-ec2-db.cecurbs9fk6o.us-east-1.rds.amazonaws.com
SOURCE_DB_PORT=5432
SOURCE_DB_USER=postgres
SOURCE_DB_NAME=learnservicedatabase
SOURCE_DB_PASSWORD=vk-db-postgres

TARGET_DB_HOST=new-db.region.rds.amazonaws.com
TARGET_DB_PORT=5432
TARGET_DB_USER=postgres
TARGET_DB_NAME=learnservicedatabase
TARGET_DB_PASSWORD=your-target-password
```

## Три шага - создать бэкап

```bash
make backup-remote
# Выбираем: 1
```

Готово! Бэкап будет сохранен в `./backups/`

## Четыре шага (опционально) - восстановить на новом инстансе

```bash
make backup-remote
# Выбираем: 3
# Следуем инструкциям (можно отредактировать хост и пароль)
```

---

## Команды

```bash
make backup-remote       # Интерактивное меню (бэкап, восстановление, проверка и т.д.)
make backup-list         # Показать список всех локальных бэкапов
```

## Безопасность

⚠️ **ВАЖНО**: Файл `.env.backup` содержит пароли и автоматически добавлен в `.gitignore`!

Никогда не коммитьте пароли в репозиторий.

---

Полная документация: [BACKUP_GUIDE.md](BACKUP_GUIDE.md)
