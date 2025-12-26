#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрационный скрипт для быстрого тестирования системы
"""

from product_parser import ProductNameParser
from brand_matcher import BrandMatcher, FlavorMatcher

def main():
    print("="*80)
    print("ДЕМОНСТРАЦИЯ СИСТЕМЫ АВТОМАТИЧЕСКОЙ КАТЕГОРИЗАЦИИ")
    print("="*80)
    print()
    
    # Проверяем наличие обученной базы
    import os
    if not os.path.exists('knowledge_base.json') or not os.path.exists('brands_db.json'):
        print("⚠️  ВНИМАНИЕ: Система не обучена!")
        print("\nСначала запустите обучение:")
        print("  python3 learning_engine.py")
        print("\nИли используйте start.py:")
        print("  python3 start.py")
        print("\nОбучение займет 2-5 минут и создаст базу знаний на основе ваших данных.")
        return
    
    # Инициализация с обученной базой
    parser = ProductNameParser('knowledge_base.json')
    brand_matcher = BrandMatcher('brands_db.json')
    flavor_matcher = FlavorMatcher('brands_db.json')
    
    # Получаем все бренды из обученной базы
    popular_brands = brand_matcher.get_all_brands()
    
    print(f"✓ База знаний загружена")
    print(f"  Количество брендов: {len(popular_brands)}")
    print(f"  Количество вкусов: {len(flavor_matcher.get_all_flavors())}")
    print()
    
    # Тестовые примеры
    test_products = [
        "Минеральная вода ЧИСТОЗЕРЬЕ ГАЗ. ПЭТ 0,5Л",
        "Напиток ДОБРЫЙ КОЛА БЕЗ САХАРА ГАЗ. ПЭТ 2Л",
        "Энергетик ADRENALINE RUSH 0,449Л",
        "Вода BONAQUA негаз. ПЭТ 1,5Л",
        "Сок J7 АПЕЛЬСИН 0,2Л",
        "ФРУКТОВЫЙ САД НЕКТАР ЯБЛОЧНЫЙ ОСВЕТЛ 1,93Л(ЛЕБЕДЯНСКИЙ):6",
        "КОКА-КОЛА напиток газ. 0,5Л",
        "Напиток АДРЕН энергетик банка 0,5Л",
        "СОК ЛЮБИМЫЙ ТОМАТ с мякотью 1л"
    ]
    
    print("Обработка тестовых товаров:\n")
    
    for i, product_name in enumerate(test_products, 1):
        print(f"{i}. Оригинал: {product_name}")
        print("-" * 80)
        
        # Парсинг
        features = parser.parse(product_name)
        
        # Поиск бренда
        brand_match = brand_matcher.match_brand(product_name, popular_brands)
        
        # Поиск вкуса
        flavor = flavor_matcher.match_flavor(product_name)
        
        # Вывод результатов
        print(f"   Бренд: {brand_match.matched_brand if brand_match else 'Не определен'}", end="")
        if brand_match:
            print(f" (уверенность: {brand_match.confidence:.1f}%, метод: {brand_match.method})")
        else:
            print()
        
        print(f"   Тип: {features.product_type if features.product_type else 'Не определен'}")
        print(f"   Вкус: {flavor if flavor else 'Не определен'}")
        print(f"   Объем: {features.volume}Л" if features.volume else "   Объем: Не определен")
        print(f"   Упаковка: {features.packaging if features.packaging else 'Не определена'}")
        print(f"   Газирование: {features.carbonation if features.carbonation else 'Не определено'}")
        print(f"   Без сахара: {'Да' if features.sugar_free else 'Нет'}")
        
        # Определяем категорию
        if features.product_type == 'water':
            category = 'вода'
        elif features.carbonation == 'carbonated' and features.product_type in ['beverage', 'cola', 'lemonade']:
            category = 'газировка'
        elif features.product_type == 'energy_drink':
            category = 'энергетик'
        else:
            category = 'прочее'
        
        print(f"   Категория: {category}")
        print()
    
    print("="*80)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("="*80)
    print()
    print("Для полноценной работы:")
    print("1. Запустите обучение: python3 learning_engine.py")
    print("2. Обработайте свои данные: python3 auto_categorizer.py -i your_file.csv")
    print()


if __name__ == "__main__":
    main()
