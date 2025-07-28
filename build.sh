#!/bin/bash
# Скрипт для сборки и публикации пакета

set -e

echo "🔧 Сборка пакета shared-models..."

# Очистка предыдущих сборок
echo "🧹 Очистка предыдущих сборок..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

# Установка зависимостей для сборки
echo "📦 Установка зависимостей для сборки..."
poetry install --with dev

# Проверка форматирования кода
echo "🎨 Проверка форматирования кода..."
poetry run black --check . || {
    echo "❌ Код не отформатирован. Запустите: poetry run black ."
    exit 1
}

# Сборка пакета
echo "🏗️ Сборка пакета..."
poetry build

# Проверка сборки
echo "✅ Проверка содержимого пакета..."
ls -la dist/

echo "🎉 Сборка завершена успешно!"
echo ""
echo "📋 Инструкции по установке:"
echo "   pip install dist/shared_models-0.1.0-py3-none-any.whl"
echo "   или"
echo "   pip install git+https://github.com/ViachaslauKazakou/shared-models.git"
echo ""
echo "📚 Документация по использованию: USAGE.md"
