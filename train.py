#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенный скрипт для обучения системы
Автоматически обучается на product1.xlsx и sku_vkus.xlsx
"""

import os
import sys
from settings import PRODUCT_FILE, SKU_FILE, validate_settings


def main():
    print("\n" + "="*80)
    print("  🎓 ОБУЧЕНИЕ СИСТЕМЫ КАТЕГОРИЗАЦИИ")
    print("="*80 + "\n")
    
    # Проверяем настройки
    if not validate_settings():
        print("\n❌ Ошибка в настройках!")
        print("Откройте файл settings.py и укажите правильные пути к файлам.")
        return 1
    
    # Проверяем наличие файлов
    if not os.path.exists(PRODUCT_FILE):
        print(f"❌ ОШИБКА: Файл не найден: {PRODUCT_FILE}")
        return 1
    
    if not os.path.exists(SKU_FILE):
        print(f"❌ ОШИБКА: Файл не найден: {SKU_FILE}")
        return 1
    
    print(f"📚 Обучение на данных из:")
    print(f"   {PRODUCT_FILE}")
    print(f"   {SKU_FILE}\n")
    
    # Импортируем после проверки
    from learning_engine import LearningEngine
    
    # Создаем движок обучения
    engine = LearningEngine(
        product_file=PRODUCT_FILE,
        sku_file=SKU_FILE,
        knowledge_base_path='knowledge_base.json',
        brands_db_path='brands_db.json'
    )
    
    # Запускаем обучение
    try:
        print("⏳ Начинается обучение (это займет 2-5 минут)...\n")
        knowledge_base = engine.learn_from_data()
        
        print("\n" + "="*80)
        print("  ✅ ОБУЧЕНИЕ ЗАВЕРШЕНО!")
        print("="*80)
        print("\nСозданы файлы:")
        print("  ✓ knowledge_base.json - база знаний")
        print("  ✓ brands_db.json      - база брендов")
        print("\nТеперь можно обрабатывать товары:")
        print("  python3 auto_categorizer.py -i new_products.csv")
        print("  или")
        print("  python3 start.py\n")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Обучение прервано пользователем\n")
        return 1
    
    except Exception as e:
        print(f"\n❌ ОШИБКА при обучении: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
