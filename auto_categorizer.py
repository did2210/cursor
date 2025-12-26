#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Главный скрипт автоматической категоризации товаров
Анализирует новые xcode и автоматически заполняет информацию о товаре
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime
import os

from product_parser import ProductNameParser, ProductFeatures
from brand_matcher import BrandMatcher, FlavorMatcher
from learning_engine import LearningEngine


class AutoCategorizer:
    """Автоматический категоризатор товаров"""
    
    def __init__(self, 
                 product_file: str,
                 sku_file: str,
                 knowledge_base_path: str = 'knowledge_base.json',
                 brands_db_path: str = 'brands_db.json',
                 auto_learn: bool = True):
        """
        Args:
            product_file: путь к файлу product1.xlsx
            sku_file: путь к файлу sku_vkus.xlsx
            knowledge_base_path: путь к базе знаний
            brands_db_path: путь к базе брендов
            auto_learn: автоматически обучаться на новых данных
        """
        self.product_file = product_file
        self.sku_file = sku_file
        self.auto_learn = auto_learn
        
        # Загружаем существующие данные
        self.product_df = pd.read_excel(product_file)
        self.sku_df = pd.read_excel(sku_file)
        
        # Инициализируем компоненты
        self.parser = ProductNameParser(knowledge_base_path)
        self.brand_matcher = BrandMatcher(brands_db_path)
        self.flavor_matcher = FlavorMatcher(brands_db_path)
        
        # Кэш известных xcode
        self.known_xcodes = set(self.product_df['xcode'].astype(str).values)
        self.known_sku_xcodes = set(self.sku_df['xcode'].astype(str).values)
        
        # Статистика
        self.stats = {
            'processed': 0,
            'new_products': 0,
            'updated_products': 0,
            'failed': 0
        }
        
        print("Автокатегоризатор инициализирован")
        print(f"Загружено существующих товаров: {len(self.product_df)}")
        print(f"Загружено SKU: {len(self.sku_df)}")
    
    def categorize_product(self, xcode: str, xname: str) -> Dict:
        """
        Категоризация одного товара
        
        Args:
            xcode: код товара
            xname: название товара
            
        Returns:
            Dict с распознанной информацией
        """
        # Парсим название
        features = self.parser.parse(xname)
        
        # Определяем бренд
        known_brands = list(self.brand_matcher.brands_db.get('brands', {}).keys())
        brand_match = self.brand_matcher.match_brand(xname, known_brands)
        
        if brand_match:
            brand = brand_match.matched_brand
            brand_confidence = brand_match.confidence
        else:
            brand = features.brand if features.brand else 'LOCAL'
            brand_confidence = 50.0
        
        # Определяем вкус
        flavor = self.flavor_matcher.match_flavor(xname)
        if not flavor:
            flavor = features.flavor if features.flavor else 'CLASSIC'
        
        # Определяем категорию
        category = self._determine_category(features, xname)
        
        # Определяем подкатегорию
        subcategory = self._determine_subcategory(features, category, xname)
        
        # Определяем категорию объема
        volume_category = self._determine_volume_category(features.volume)
        
        # Определяем производителя
        proizvod = self._determine_producer(brand, xname)
        
        # Определяем SKU
        sku = self._determine_sku(brand, flavor)
        
        # Формируем результат
        result = {
            'xcode': xcode,
            'xname': xname,
            'category': category,
            'brand': brand,
            'brand_confidence': brand_confidence,
            'litrag': features.volume if features.volume else 0.0,
            'catlitrag': volume_category,
            'proizvod': proizvod,
            'brand2': brand if brand != 'LOCAL' else 'LOCAL',
            'proizvod2': proizvod if proizvod != 'LOCAL' else 'LOCAL',
            'packqnt': 1,  # по умолчанию
            'pack': features.packaging if features.packaging else 'CAN',
            'subcategory': subcategory,
            'sku': sku,
            'vkus': flavor,
            'sugar_free': features.sugar_free,
            'carbonation': features.carbonation,
            'product_type': features.product_type,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return result
    
    def _determine_category(self, features: ProductFeatures, xname: str) -> str:
        """Определение основной категории"""
        xname_upper = xname.upper()
        
        # Правила определения категории
        if 'ВОДА' in xname_upper and ('МИНЕРАЛЬНАЯ' in xname_upper or 'ПИТЬЕВАЯ' in xname_upper):
            return 'вода'
        
        if features.carbonation == 'carbonated' and features.product_type in ['beverage', 'cola', 'lemonade']:
            return 'газировка'
        
        if features.product_type in ['juice', 'nectar', 'mors']:
            return 'прочее'
        
        if 'ЭНЕРГЕТИК' in xname_upper or features.product_type == 'energy_drink':
            return 'энергетик'
        
        if features.product_type in ['tea', 'coffee']:
            return 'прочее'
        
        # По умолчанию
        if features.carbonation == 'carbonated':
            return 'газировка'
        
        return 'прочее'
    
    def _determine_subcategory(self, features: ProductFeatures, category: str, xname: str) -> str:
        """Определение подкатегории"""
        xname_upper = xname.upper()
        volume = features.volume if features.volume else 0.0
        
        # Газировки
        if category == 'газировка':
            # Проверяем бренд
            if any(brand in xname_upper for brand in ['COCA-COLA', 'PEPSI', 'SCHWEPPES', 'SPRITE', 'FANTA']):
                if volume < 0.8:
                    return 'Газированные напитки мировых брендов менее 0,8л'
                else:
                    return 'Газированные напитки мировых брендов более 0,8л'
            else:
                if volume < 0.8:
                    return 'Газированные напитки российских брендов менее 0,8л'
                else:
                    return 'Газированные напитки российских брендов более 0,8л'
        
        # Вода
        if category == 'вода':
            if 'МИНЕРАЛЬНАЯ' in xname_upper:
                if 'ГАЗ' in xname_upper:
                    return 'Вода минеральная газированная'
                else:
                    return 'Вода минеральная негазированная'
            else:
                return 'Вода питьевая'
        
        # Соки и нектары
        if features.product_type in ['juice', 'nectar']:
            if volume <= 0.5:
                return 'Соки и нектары менее 0,5л'
            elif volume <= 1.5:
                return 'Соки и нектары более 0,5л и до 1,5л'
            else:
                return 'Соки и нектары более 1,5л'
        
        # Энергетики
        if category == 'энергетик':
            return 'Энергетические напитки'
        
        return 'Прочие напитки'
    
    def _determine_volume_category(self, volume: Optional[float]) -> str:
        """Определение категории объема"""
        if not volume:
            return 'неизвестно'
        
        if volume < 0.4:
            return '0-0,4л'
        elif volume < 0.6:
            return '0,4-0,6л'
        elif volume < 1.0:
            return '0,6-1л'
        elif volume < 1.5:
            return '1,0-1,5л'
        elif volume < 2.0:
            return '1,5-2,0л'
        elif volume < 2.5:
            return '2,0-2,5л'
        else:
            return '2,5л+'
    
    def _determine_producer(self, brand: str, xname: str) -> str:
        """Определение производителя"""
        # Крупные производители
        producers_map = {
            'COCA-COLA': 'COCA-COLA',
            'PEPSI': 'PEPSICO',
            'ДОБРЫЙ': 'PEPSICO',
            'ФРУКТОВЫЙ САД': 'PEPSICO',
            'J7': 'PEPSICO',
            'ADRENALINE': 'ADRENALINE RUSH',
            'RICH': 'COCA-COLA',
            'BONAQUA': 'COCA-COLA',
            'SCHWEPPES': 'COCA-COLA'
        }
        
        brand_upper = brand.upper()
        
        # Проверяем известных производителей
        for brand_key, producer in producers_map.items():
            if brand_key in brand_upper:
                return producer
        
        # Ищем производителя в скобках
        import re
        match = re.search(r'\(([^)]+)\)', xname)
        if match:
            producer_candidate = match.group(1).strip().upper()
            # Убираем служебные слова
            if not any(x in producer_candidate for x in [':', 'ООО', 'ОАО', 'ЗАО']):
                return producer_candidate
        
        return 'LOCAL'
    
    def _determine_sku(self, brand: str, flavor: str) -> str:
        """Определение SKU"""
        if brand == 'LOCAL' or not brand:
            return f"LOCAL {flavor}" if flavor else "LOCAL"
        
        return f"{brand} {flavor}" if flavor else brand
    
    def process_new_products(self, new_products: List[Dict]) -> pd.DataFrame:
        """
        Обработка списка новых товаров
        
        Args:
            new_products: список dict с полями 'xcode' и 'xname'
            
        Returns:
            DataFrame с распознанной информацией
        """
        results = []
        
        print(f"\nОбработка {len(new_products)} новых товаров...\n")
        
        for i, product in enumerate(new_products, 1):
            xcode = str(product['xcode'])
            xname = product['xname']
            
            try:
                result = self.categorize_product(xcode, xname)
                results.append(result)
                self.stats['processed'] += 1
                
                # Вывод прогресса
                if i % 10 == 0 or i == len(new_products):
                    print(f"Обработано: {i}/{len(new_products)}")
                    print(f"  Последний: {xname}")
                    print(f"  -> Бренд: {result['brand']} (уверенность: {result['brand_confidence']:.1f}%)")
                    print(f"  -> Категория: {result['category']}")
                    print(f"  -> Вкус: {result['vkus']}")
                    print()
                
            except Exception as e:
                print(f"ОШИБКА при обработке {xcode}: {xname}")
                print(f"  {str(e)}")
                self.stats['failed'] += 1
        
        return pd.DataFrame(results)
    
    def check_for_new_products(self, input_file: str) -> List[Dict]:
        """
        Проверка входного файла на наличие новых товаров
        
        Args:
            input_file: путь к файлу с товарами для проверки
            
        Returns:
            Список новых товаров
        """
        # Читаем входной файл
        if input_file.endswith('.xlsx'):
            input_df = pd.read_excel(input_file)
        elif input_file.endswith('.csv'):
            input_df = pd.read_csv(input_file)
        else:
            raise ValueError("Поддерживаются только .xlsx и .csv файлы")
        
        # Проверяем наличие необходимых колонок
        if 'xcode' not in input_df.columns or 'xname' not in input_df.columns:
            raise ValueError("Файл должен содержать колонки 'xcode' и 'xname'")
        
        # Находим новые товары
        new_products = []
        
        for _, row in input_df.iterrows():
            xcode = str(row['xcode'])
            if xcode not in self.known_xcodes:
                new_products.append({
                    'xcode': xcode,
                    'xname': row['xname']
                })
        
        print(f"Найдено новых товаров: {len(new_products)} из {len(input_df)}")
        
        return new_products
    
    def update_databases(self, results_df: pd.DataFrame):
        """Обновление баз данных с новыми товарами"""
        print("\nОбновление баз данных...")
        
        # Добавляем в product_df
        product_cols = ['xcode', 'xname', 'category', 'brand', 'litrag', 
                       'catlitrag', 'proizvod', 'brand2', 'proizvod2', 
                       'packqnt', 'pack', 'subcategory']
        
        new_product_rows = results_df[product_cols].copy()
        new_product_rows['id'] = range(
            self.product_df['id'].max() + 1 if len(self.product_df) > 0 else 1,
            self.product_df['id'].max() + 1 + len(new_product_rows) if len(self.product_df) > 0 else len(new_product_rows) + 1
        )
        new_product_rows['changed'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.000')
        
        self.product_df = pd.concat([self.product_df, new_product_rows], ignore_index=True)
        
        # Добавляем в sku_df
        sku_cols = ['xcode', 'xname', 'sku', 'vkus', 'pack']
        
        new_sku_rows = results_df[sku_cols].copy()
        new_sku_rows['id'] = range(
            self.sku_df['id'].max() + 1 if len(self.sku_df) > 0 else 1,
            self.sku_df['id'].max() + 1 + len(new_sku_rows) if len(self.sku_df) > 0 else len(new_sku_rows) + 1
        )
        
        self.sku_df = pd.concat([self.sku_df, new_sku_rows], ignore_index=True)
        
        self.stats['new_products'] = len(new_product_rows)
        
        print(f"Добавлено в product: {len(new_product_rows)} товаров")
        print(f"Добавлено в SKU: {len(new_sku_rows)} записей")
    
    def save_results(self, output_product_file: str = None, output_sku_file: str = None):
        """Сохранение результатов"""
        if output_product_file is None:
            output_product_file = self.product_file.replace('.xlsx', '_updated.xlsx')
        
        if output_sku_file is None:
            output_sku_file = self.sku_file.replace('.xlsx', '_updated.xlsx')
        
        print(f"\nСохранение результатов...")
        self.product_df.to_excel(output_product_file, index=False)
        print(f"  Сохранено в: {output_product_file}")
        
        self.sku_df.to_excel(output_sku_file, index=False)
        print(f"  Сохранено в: {output_sku_file}")
    
    def print_statistics(self):
        """Вывод статистики"""
        print("\n" + "="*80)
        print("СТАТИСТИКА ОБРАБОТКИ")
        print("="*80)
        print(f"Обработано товаров: {self.stats['processed']}")
        print(f"Новых товаров добавлено: {self.stats['new_products']}")
        print(f"Обновлено товаров: {self.stats['updated_products']}")
        print(f"Ошибок: {self.stats['failed']}")
        
        if self.stats['processed'] > 0:
            success_rate = (self.stats['processed'] - self.stats['failed']) / self.stats['processed'] * 100
            print(f"Успешность: {success_rate:.1f}%")
        
        print("="*80 + "\n")


def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Автоматическая категоризация товаров')
    parser.add_argument('--input', '-i', required=True, help='Входной файл с новыми товарами')
    parser.add_argument('--product', '-p', default='product1.xlsx', help='Файл с товарами')
    parser.add_argument('--sku', '-s', default='sku_vkus.xlsx', help='Файл с SKU')
    parser.add_argument('--train', '-t', action='store_true', help='Сначала обучить модель')
    parser.add_argument('--output-product', '-op', help='Выходной файл для товаров')
    parser.add_argument('--output-sku', '-os', help='Выходной файл для SKU')
    
    args = parser.parse_args()
    
    # Если нужно обучение
    if args.train:
        print("Обучение модели на существующих данных...")
        engine = LearningEngine(
            product_file=args.product,
            sku_file=args.sku,
            knowledge_base_path='knowledge_base.json',
            brands_db_path='brands_db.json'
        )
        engine.learn_from_data()
        print("\nОбучение завершено!\n")
    
    # Создаем категоризатор
    categorizer = AutoCategorizer(
        product_file=args.product,
        sku_file=args.sku,
        knowledge_base_path='knowledge_base.json',
        brands_db_path='brands_db.json'
    )
    
    # Проверяем на новые товары
    new_products = categorizer.check_for_new_products(args.input)
    
    if not new_products:
        print("Новых товаров не найдено!")
        return
    
    # Обрабатываем новые товары
    results_df = categorizer.process_new_products(new_products)
    
    # Обновляем базы данных
    categorizer.update_databases(results_df)
    
    # Сохраняем результаты
    categorizer.save_results(args.output_product, args.output_sku)
    
    # Выводим статистику
    categorizer.print_statistics()
    
    print("\nГотово! Проверьте выходные файлы.")


if __name__ == "__main__":
    main()
