#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование системы на файле Bristol
"""

import pandas as pd
from product_parser import ProductNameParser
from brand_matcher import BrandMatcher, FlavorMatcher
import os

print("="*80)
print("ТЕСТИРОВАНИЕ СИСТЕМЫ НА ФАЙЛЕ BRISTOL")
print("="*80)

# Читаем Bristol файл
print("\n1. Загрузка данных Bristol...")
bristol_df = pd.read_excel('BRISTOL_ба_напитки_11.2025_ч1.xlsx')
print(f"   ✓ Загружено товаров: {len(bristol_df)}")

# Читаем обучающие данные
print("\n2. Загрузка обучающих данных...")
product_df = pd.read_excel('product1.xlsx')
sku_df = pd.read_excel('sku_vkus.xlsx')
print(f"   ✓ product1.xlsx: {len(product_df)} товаров")
print(f"   ✓ sku_vkus.xlsx: {len(sku_df)} записей")

# Инициализируем компоненты БЕЗ загрузки JSON (создаем временные)
print("\n3. Инициализация системы...")
parser = ProductNameParser()
brand_matcher = BrandMatcher()
flavor_matcher = FlavorMatcher()

# Быстрое обучение на первых 1000 товаров
print("\n4. Быстрое обучение на sample данных...")
print("   (Для полного обучения запустите: python3 train.py)")

# Извлекаем бренды из product1.xlsx
brands_set = set()
for _, row in product_df.head(1000).iterrows():
    brand = str(row.get('brand', '')).strip().upper()
    if brand and brand not in ['LOCAL', 'NAN']:
        brands_set.add(brand)
        brand_matcher.add_brand_to_db(brand)

print(f"   ✓ Изучено брендов: {len(brands_set)}")

# Извлекаем вкусы из sku_vkus.xlsx
flavors_set = set()
for _, row in sku_df.head(1000).iterrows():
    vkus = str(row.get('vkus', '')).strip().upper()
    if vkus and vkus not in ['LOCAL', 'CLASSIC', 'NAN']:
        flavors_set.add(vkus)
        flavor_matcher.add_flavor(vkus)

print(f"   ✓ Изучено вкусов: {len(flavors_set)}")

# Тестируем на Bristol товарах
print("\n5. Тестирование на товарах Bristol...")
print("="*80)

known_brands = list(brands_set)
results = []

for i, row in bristol_df.head(20).iterrows():
    xcode = row['Xcode']
    xname = row['Xname']
    
    print(f"\n{i+1}. xcode: {xcode}")
    print(f"   xname: {xname}")
    
    # Парсим название
    features = parser.parse(xname)
    
    # Ищем бренд
    brand_match = brand_matcher.match_brand(xname, known_brands)
    
    # Ищем вкус
    flavor = flavor_matcher.match_flavor(xname)
    
    # Результаты
    if brand_match:
        print(f"   ✓ БРЕНД: {brand_match.matched_brand} ({brand_match.confidence:.0f}%, {brand_match.method})")
    else:
        print(f"   ❌ БРЕНД: не определен")
    
    if features.volume:
        print(f"   ✓ ОБЪЕМ: {features.volume}Л")
    else:
        print(f"   ⚠️  ОБЪЕМ: не определен")
    
    if features.packaging:
        print(f"   ✓ УПАКОВКА: {features.packaging}")
    else:
        print(f"   ⚠️  УПАКОВКА: не определена")
    
    if flavor:
        print(f"   ✓ ВКУС: {flavor}")
    
    if features.product_type:
        print(f"   ✓ ТИП: {features.product_type}")
    
    # Сохраняем результат
    results.append({
        'xcode': xcode,
        'xname': xname,
        'brand': brand_match.matched_brand if brand_match else 'LOCAL',
        'brand_confidence': brand_match.confidence if brand_match else 0,
        'volume': features.volume,
        'packaging': features.packaging,
        'flavor': flavor,
        'product_type': features.product_type,
        'carbonation': features.carbonation,
        'sugar_free': features.sugar_free
    })

# Статистика
print("\n" + "="*80)
print("СТАТИСТИКА РАСПОЗНАВАНИЯ")
print("="*80)

brands_found = sum(1 for r in results if r['brand'] != 'LOCAL')
volumes_found = sum(1 for r in results if r['volume'])
packaging_found = sum(1 for r in results if r['packaging'])

total = len(results)
print(f"Обработано товаров: {total}")
print(f"Бренды определены: {brands_found}/{total} ({brands_found/total*100:.1f}%)")
print(f"Объемы определены: {volumes_found}/{total} ({volumes_found/total*100:.1f}%)")
print(f"Упаковка определена: {packaging_found}/{total} ({packaging_found/total*100:.1f}%)")

# Сохраняем результаты
results_df = pd.DataFrame(results)
results_df.to_csv('bristol_test_results.csv', index=False)
print(f"\n✓ Результаты сохранены в: bristol_test_results.csv")

print("\n" + "="*80)
print("ТЕСТ ЗАВЕРШЕН!")
print("="*80)
print("\nДля полноценной работы:")
print("1. Запустите полное обучение: python3 train.py")
print("2. Обработайте все товары: python3 auto_categorizer.py -i bristol_input.csv")
