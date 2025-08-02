#!/bin/bash

# Скрипт для создания нового релиза
# Использование: ./scripts/create-release.sh [patch|minor|major]

set -e

# Функция для отображения справки
show_help() {
    echo "Использование: $0 [patch|minor|major]"
    echo ""
    echo "Опции:"
    echo "  patch  - Увеличить патч версию (0.1.1 -> 0.1.2)"
    echo "  minor  - Увеличить минорную версию (0.1.1 -> 0.2.0)"
    echo "  major  - Увеличить мажорную версию (0.1.1 -> 1.0.0)"
    echo ""
    echo "Примеры:"
    echo "  $0 patch   # Багфиксы"
    echo "  $0 minor   # Новые функции"
    echo "  $0 major   # Кардинальные изменения"
}

# Проверка аргументов
if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

VERSION_TYPE=$1

# Проверка валидности типа версии
if [[ "$VERSION_TYPE" != "patch" && "$VERSION_TYPE" != "minor" && "$VERSION_TYPE" != "major" ]]; then
    echo "❌ Ошибка: Неверный тип версии '$VERSION_TYPE'"
    echo ""
    show_help
    exit 1
fi

# Проверка что мы в git репозитории
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Ошибка: Не найден git репозиторий"
    exit 1
fi

# Проверка что нет незакоммиченных изменений
if ! git diff-index --quiet HEAD --; then
    echo "❌ Ошибка: Есть незакоммиченные изменения"
    echo "Пожалуйста, закоммитьте все изменения перед созданием релиза"
    exit 1
fi

# Получение текущей версии из pyproject.toml
CURRENT_VERSION=$(poetry run python3 -c "import toml; print(toml.load('pyproject.toml')['project']['version'])" 2>/dev/null)

if [ $? -ne 0 ]; then
    echo "❌ Ошибка: Не удалось прочитать текущую версию из pyproject.toml"
    echo "Убедитесь, что установлены Poetry и пакет toml"
    exit 1
fi

echo "📦 Текущая версия: $CURRENT_VERSION"

# Разбор версии на компоненты
IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}

# Увеличение версии
case $VERSION_TYPE in
    "major")
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    "minor")
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    "patch")
        PATCH=$((PATCH + 1))
        ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
echo "🚀 Новая версия: $NEW_VERSION"

# Подтверждение от пользователя
read -p "Продолжить создание релиза $NEW_VERSION? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Отменено пользователем"
    exit 1
fi

# Обновление версии в pyproject.toml
echo "📝 Обновление версии в pyproject.toml..."
sed -i.bak "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml

# Проверка что версия обновилась
UPDATED_VERSION=$(poetry run python3 -c "import toml; print(toml.load('pyproject.toml')['project']['version'])")
if [ "$UPDATED_VERSION" != "$NEW_VERSION" ]; then
    echo "❌ Ошибка: Не удалось обновить версию в pyproject.toml"
    # Восстановление из бэкапа
    mv pyproject.toml.bak pyproject.toml
    exit 1
fi

# Удаление бэкапа
rm pyproject.toml.bak

# Создание коммита
echo "💾 Создание коммита..."
git add pyproject.toml
git commit -m "Bump version to $NEW_VERSION"

# Создание тега
echo "🏷️  Создание тега v$NEW_VERSION..."
git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION"

# Push изменений
echo "📤 Отправка изменений в репозиторий..."
git push origin main
git push origin "v$NEW_VERSION"

echo ""
echo "✅ Релиз $NEW_VERSION успешно создан!"
echo ""
echo "🔗 Ссылки:"
echo "   - Тег: https://github.com/ViachaslauKazakou/shared-models/releases/tag/v$NEW_VERSION"
echo "   - Сравнение: https://github.com/ViachaslauKazakou/shared-models/compare/v$CURRENT_VERSION...v$NEW_VERSION"
echo ""
echo "⏳ GitHub Actions создаст релиз автоматически в течение нескольких минут"
