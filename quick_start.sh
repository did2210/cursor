#!/bin/bash
# Скрипт быстрого старта для системы автоматической категоризации

echo "=========================================="
echo "Система Автоматической Категоризации Товаров"
echo "=========================================="
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "ОШИБКА: Python3 не найден!"
    exit 1
fi

echo "✓ Python найден: $(python3 --version)"
echo ""

# Установка зависимостей
echo "Шаг 1: Установка зависимостей..."
pip install -q -r requirements.txt
echo "✓ Зависимости установлены"
echo ""

# Обучение системы
echo "Шаг 2: Обучение системы на существующих данных..."
python3 learning_engine.py
echo ""

# Тестирование на примере
echo "Шаг 3: Тестирование на примере..."
python3 auto_categorizer.py -i example_input.csv -p product1.xlsx -s sku_vkus.xlsx
echo ""

echo "=========================================="
echo "Готово! Система готова к работе."
echo "=========================================="
echo ""
echo "Для обработки своих данных используйте:"
echo "python3 auto_categorizer.py -i your_file.csv -p product1.xlsx -s sku_vkus.xlsx"
echo ""
