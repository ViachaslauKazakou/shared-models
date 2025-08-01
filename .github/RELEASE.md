# GitHub Actions Workflows для Релизов

В проекте настроены два GitHub Actions workflow для автоматизации создания релизов:

## 1. Автоматическое создание тегов (`auto-tag.yml`)

### Как работает:
- **Триггер**: При изменении файла `pyproject.toml` в ветке `main`
- **Действия**: 
  - Извлекает версию из `pyproject.toml`
  - Проверяет, существует ли уже тег с этой версией
  - Если тег не существует, создает новый тег `v{версия}` и пушит его

### Использование:
1. Измените версию в `pyproject.toml`:
   ```toml
   [project]
   version = "0.1.3"  # Увеличьте версию
   ```
2. Сделайте commit и push в ветку `main`
3. GitHub Actions автоматически создаст тег `v0.1.3`

## 2. Создание релизов (`release.yml`)

### Как работает:
- **Триггер**: При создании тега с префиксом `v*` (например, `v1.0.0`)
- **Действия**:
  - Запускает тесты
  - Собирает пакет с помощью Poetry
  - Генерирует changelog на основе коммитов
  - Создает GitHub Release с артефактами
  - Опционально публикует в PyPI (для стабильных версий)

### Особенности:
- **Changelog**: Автоматически генерируется из коммитов между тегами
- **Prerelease**: Версии с `alpha`, `beta`, `rc` помечаются как pre-release
- **Артефакты**: Включает `.whl` и `.tar.gz` файлы
- **PyPI**: Публикация только для стабильных версий (не alpha/beta/rc)

## Настройка секретов (опционально)

Для публикации в PyPI добавьте секрет в настройках репозитория:

1. Перейдите в `Settings` → `Secrets and variables` → `Actions`
2. Добавьте секрет `PYPI_TOKEN` с токеном от PyPI

## Полный процесс релиза

### Автоматический способ:
1. Измените версию в `pyproject.toml`
2. Commit и push в `main`
3. Дождитесь автоматического создания тега
4. Дождитесь автоматического создания релиза

### Ручной способ:
1. Создайте тег вручную:
   ```bash
   git tag -a v0.1.3 -m "Release version 0.1.3"
   git push origin v0.1.3
   ```
2. GitHub Actions создаст релиз автоматически

## Примеры версий

- `v1.0.0` - стабильный релиз (будет опубликован в PyPI)
- `v1.0.0-alpha.1` - альфа версия (prerelease, не будет опубликован в PyPI)
- `v1.0.0-beta.1` - бета версия (prerelease)
- `v1.0.0-rc.1` - release candidate (prerelease)

## Структура changelog

Changelog генерируется автоматически и включает:
- Список коммитов между версиями
- Короткие хеши коммитов
- Исключает merge коммиты

Пример:
```
## Changes

- Add new feature for user authentication (a1b2c3d)
- Fix bug in database connection (e4f5g6h)
- Update documentation (i7j8k9l)
```
