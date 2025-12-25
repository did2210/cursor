#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для обучения системы на существующих данных
Анализирует product1.xlsx и sku_vkus.xlsx для построения базы знаний
"""

import pandas as pd
import json
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
import re
from product_parser import ProductNameParser, ProductFeatures
from brand_matcher import BrandMatcher, FlavorMatcher
from rapidfuzz import fuzz


class LearningEngine:
    """Движок машинного обучения на исторических данных"""
    
    def __init__(self, product_file: str, sku_file: str, 
                 knowledge_base_path: str = 'knowledge_base.json',
                 brands_db_path: str = 'brands_db.json'):
        self.product_file = product_file
        self.sku_file = sku_file
        self.knowledge_base_path = knowledge_base_path
        self.brands_db_path = brands_db_path
        
        # Компоненты системы
        self.parser = ProductNameParser(knowledge_base_path)
        self.brand_matcher = BrandMatcher(brands_db_path)
        self.flavor_matcher = FlavorMatcher()
        
        # Статистика обучения
        self.stats = {
            'total_products': 0,
            'brands_learned': 0,
            'flavors_learned': 0,
            'patterns_learned': 0,
            'categories_learned': 0
        }
        
        # Базы знаний
        self.knowledge_base = {
            'brands': {},
            'flavors': {},
            'categories': {},
            'volume_categories': {},
            'packaging_types': {},
            'brand_patterns': {},
            'flavor_patterns': {},
            'product_types': {}
        }
    
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Загрузка данных из Excel файлов"""
        print("Загрузка данных...")
        product_df = pd.read_excel(self.product_file)
        sku_df = pd.read_excel(self.sku_file)
        
        print(f"Загружено продуктов: {len(product_df)}")
        print(f"Загружено SKU: {len(sku_df)}")
        
        return product_df, sku_df
    
    def learn_from_data(self):
        """Основной метод обучения на данных"""
        print("\n" + "="*80)
        print("НАЧАЛО ОБУЧЕНИЯ СИСТЕМЫ")
        print("="*80 + "\n")
        
        product_df, sku_df = self.load_data()
        
        self.stats['total_products'] = len(product_df)
        
        # 1. Обучение на брендах
        print("Этап 1: Обучение распознаванию брендов...")
        self._learn_brands(product_df)
        
        # 2. Обучение на вкусах
        print("\nЭтап 2: Обучение распознаванию вкусов...")
        self._learn_flavors(sku_df)
        
        # 3. Обучение на категориях
        print("\nЭтап 3: Обучение категориям товаров...")
        self._learn_categories(product_df)
        
        # 4. Обучение на объемах
        print("\nЭтап 4: Обучение категориям объемов...")
        self._learn_volumes(product_df)
        
        # 5. Анализ паттернов в названиях
        print("\nЭтап 5: Анализ паттернов в названиях...")
        self._learn_patterns(product_df, sku_df)
        
        # 6. Обучение на типах упаковки
        print("\nЭтап 6: Обучение типам упаковки...")
        self._learn_packaging(product_df)
        
        # 7. Сохранение базы знаний
        print("\nСохранение базы знаний...")
        self._save_knowledge_base()
        
        # Вывод статистики
        self._print_statistics()
        
        return self.knowledge_base
    
    def _learn_brands(self, df: pd.DataFrame):
        """Обучение на брендах"""
        brand_examples = defaultdict(list)
        brand_variations = defaultdict(set)
        
        print("  Анализ брендов из данных...")
        processed = 0
        
        for _, row in df.iterrows():
            xname = str(row.get('xname', '')).upper()
            brand = str(row.get('brand', '')).strip()
            
            if brand and brand != 'LOCAL' and brand != 'nan':
                brand_upper = brand.upper()
                brand_examples[brand_upper].append(xname)
                
                # Извлекаем вариации написания бренда из xname
                # Ищем бренд в разных формах
                if brand_upper in xname:
                    # Извлекаем слова вокруг бренда
                    words = re.findall(r'\b[А-ЯA-Z][А-ЯA-Z0-9\-]*\b', xname)
                    for word in words:
                        # Если слово похоже на бренд (fuzzy matching)
                        if len(word) >= 3:
                            ratio = fuzz.ratio(word, brand_upper)
                            if ratio >= 75:  # Похоже на бренд
                                brand_variations[brand_upper].add(word)
                
                # Добавляем бренд в базу
                self.brand_matcher.add_brand_to_db(brand_upper)
                
                # Учим систему на примере
                self.brand_matcher.learn_brand_variation(xname, brand_upper)
                
                processed += 1
                if processed % 1000 == 0:
                    print(f"    Обработано: {processed}/{len(df)}")
        
        # Добавляем вариации в базу брендов
        for brand, variations in brand_variations.items():
            for variation in variations:
                if variation != brand:  # Не добавляем сам бренд как вариацию
                    self.brand_matcher.learn_brand_variation(variation, brand)
        
        self.stats['brands_learned'] = len(brand_examples)
        
        # Сохраняем примеры в базу знаний
        self.knowledge_base['brands'] = {
            brand: {
                'count': len(examples),
                'examples': examples[:10],
                'variations': list(brand_variations.get(brand, []))[:20]
            }
            for brand, examples in brand_examples.items()
        }
        
        print(f"\n  ✓ Изучено брендов: {self.stats['brands_learned']}")
        print(f"  ✓ Обработано товаров: {processed}")
        print(f"\n  📊 Топ-20 брендов по популярности:")
        top_brands = sorted(brand_examples.items(), key=lambda x: len(x[1]), reverse=True)[:20]
        for i, (brand, examples) in enumerate(top_brands, 1):
            variations = brand_variations.get(brand, set())
            var_str = f" ({len(variations)} вариаций)" if variations else ""
            print(f"    {i:2d}. {brand:30s} - {len(examples):5d} товаров{var_str}")
    
    def _learn_flavors(self, df: pd.DataFrame):
        """Обучение на вкусах"""
        flavor_examples = defaultdict(list)
        flavor_aliases = defaultdict(set)
        
        for _, row in df.iterrows():
            xname = str(row.get('xname', '')).upper()
            vkus = str(row.get('vkus', '')).strip()
            
            if vkus and vkus not in ['LOCAL', 'CLASSIC', 'nan']:
                vkus_upper = vkus.upper()
                flavor_examples[vkus_upper].append(xname)
                
                # Добавляем вкус в FlavorMatcher
                self.flavor_matcher.add_flavor(vkus_upper)
                
                # Пытаемся извлечь алиасы из названия
                # Например, из "ЯБЛОКО" можем найти "APPLE", "ЯБЛОЧНЫЙ"
                words = re.findall(r'\b[А-ЯA-Z]{3,}\b', xname)
                for word in words:
                    if fuzz.ratio(word, vkus_upper) >= 70:
                        flavor_aliases[vkus_upper].add(word)
        
        # Сохраняем алиасы в FlavorMatcher
        for flavor, aliases in flavor_aliases.items():
            self.flavor_matcher.add_flavor(flavor, list(aliases))
        
        # Сохраняем базу вкусов
        self.flavor_matcher.save_flavors_db()
        
        self.stats['flavors_learned'] = len(flavor_examples)
        
        # Сохраняем в базу знаний
        self.knowledge_base['flavors'] = {
            flavor: {
                'count': len(examples),
                'examples': examples[:10],
                'aliases': list(flavor_aliases.get(flavor, []))
            }
            for flavor, examples in flavor_examples.items()
        }
        
        print(f"  Изучено вкусов: {self.stats['flavors_learned']}")
        print(f"  Топ-20 вкусов:")
        top_flavors = sorted(flavor_examples.items(), key=lambda x: len(x[1]), reverse=True)[:20]
        for flavor, examples in top_flavors:
            aliases = flavor_aliases.get(flavor, set())
            aliases_str = f" (алиасы: {', '.join(list(aliases)[:3])})" if aliases else ""
            print(f"    {flavor}: {len(examples)} товаров{aliases_str}")
    
    def _learn_categories(self, df: pd.DataFrame):
        """Обучение на категориях"""
        category_examples = defaultdict(list)
        subcategory_examples = defaultdict(list)
        
        for _, row in df.iterrows():
            xname = str(row.get('xname', '')).upper()
            category = str(row.get('category', '')).strip()
            subcategory = str(row.get('subcategory', '')).strip()
            
            if category and category != 'nan':
                category_examples[category].append(xname)
            
            if subcategory and subcategory != 'nan':
                subcategory_examples[subcategory].append(xname)
        
        self.stats['categories_learned'] = len(category_examples)
        
        self.knowledge_base['categories'] = {
            'main_categories': {
                cat: {
                    'count': len(examples),
                    'examples': examples[:5]
                }
                for cat, examples in category_examples.items()
            },
            'subcategories': {
                subcat: {
                    'count': len(examples),
                    'examples': examples[:5]
                }
                for subcat, examples in subcategory_examples.items()
            }
        }
        
        print(f"  Изучено категорий: {len(category_examples)}")
        print(f"  Изучено подкатегорий: {len(subcategory_examples)}")
    
    def _learn_volumes(self, df: pd.DataFrame):
        """Обучение на объемах"""
        volume_categories = defaultdict(list)
        
        for _, row in df.iterrows():
            catlitrag = str(row.get('catlitrag', '')).strip()
            litrag = row.get('litrag', None)
            
            if catlitrag and catlitrag != 'nan':
                if litrag and not pd.isna(litrag):
                    volume_categories[catlitrag].append(float(litrag))
        
        # Вычисляем статистику по категориям объемов
        self.knowledge_base['volume_categories'] = {
            cat: {
                'count': len(volumes),
                'min': min(volumes) if volumes else 0,
                'max': max(volumes) if volumes else 0,
                'avg': sum(volumes) / len(volumes) if volumes else 0
            }
            for cat, volumes in volume_categories.items()
        }
        
        print(f"  Изучено категорий объемов: {len(volume_categories)}")
        for cat, info in self.knowledge_base['volume_categories'].items():
            print(f"    {cat}: {info['min']:.2f}Л - {info['max']:.2f}Л (среднее: {info['avg']:.2f}Л)")
    
    def _learn_patterns(self, product_df: pd.DataFrame, sku_df: pd.DataFrame):
        """Анализ паттернов в названиях товаров"""
        
        print("  Анализ паттернов в названиях...")
        
        # Паттерны для брендов - где они обычно находятся в названии
        brand_positions = []
        
        # Извлекаем структуру xname
        xname_patterns = {
            'has_parentheses': 0,  # Есть скобки ()
            'has_colon': 0,        # Есть двоеточие :
            'has_volume': 0,       # Есть объем (Л, МЛ)
            'has_packaging': 0,    # Есть упаковка (ПЭТ, СТЕКЛО)
            'total': 0
        }
        
        for _, row in product_df.iterrows():
            xname = str(row.get('xname', '')).upper()
            brand = str(row.get('brand', '')).strip().upper()
            
            xname_patterns['total'] += 1
            
            if '(' in xname:
                xname_patterns['has_parentheses'] += 1
            if ':' in xname:
                xname_patterns['has_colon'] += 1
            if 'Л' in xname or 'ML' in xname:
                xname_patterns['has_volume'] += 1
            if any(pkg in xname for pkg in ['ПЭТ', 'PET', 'СТЕКЛО', 'БАНКА', 'CAN']):
                xname_patterns['has_packaging'] += 1
            
            if brand and brand != 'LOCAL' and brand != 'nan' and brand in xname:
                position = xname.index(brand)
                relative_position = position / len(xname) if len(xname) > 0 else 0
                brand_positions.append(relative_position)
        
        # Паттерны для вкусов
        flavor_keywords = Counter()
        flavor_positions = []
        
        for _, row in sku_df.iterrows():
            xname = str(row.get('xname', '')).upper()
            vkus = str(row.get('vkus', '')).strip().upper()
            
            if vkus and vkus not in ['LOCAL', 'CLASSIC', 'nan']:
                # Ищем ключевые слова вокруг вкуса
                if vkus in xname:
                    idx = xname.index(vkus)
                    position = idx / len(xname) if len(xname) > 0 else 0
                    flavor_positions.append(position)
                    
                    # Берем слова до и после
                    words_before = re.findall(r'\b\w+\b', xname[:idx])[-2:] if idx > 0 else []
                    words_after = re.findall(r'\b\w+\b', xname[idx:])[:2]
                    
                    for word in words_before + words_after:
                        if len(word) > 2:
                            flavor_keywords[word] += 1
        
        # Сохраняем паттерны
        self.knowledge_base['xname_structure'] = {
            'parentheses_ratio': xname_patterns['has_parentheses'] / xname_patterns['total'] if xname_patterns['total'] > 0 else 0,
            'colon_ratio': xname_patterns['has_colon'] / xname_patterns['total'] if xname_patterns['total'] > 0 else 0,
            'volume_ratio': xname_patterns['has_volume'] / xname_patterns['total'] if xname_patterns['total'] > 0 else 0,
            'packaging_ratio': xname_patterns['has_packaging'] / xname_patterns['total'] if xname_patterns['total'] > 0 else 0,
        }
        
        self.knowledge_base['brand_patterns'] = {
            'typical_positions': {
                'beginning': sum(1 for p in brand_positions if p < 0.3) / len(brand_positions) if brand_positions else 0,
                'middle': sum(1 for p in brand_positions if 0.3 <= p < 0.7) / len(brand_positions) if brand_positions else 0,
                'end': sum(1 for p in brand_positions if p >= 0.7) / len(brand_positions) if brand_positions else 0
            }
        }
        
        self.knowledge_base['flavor_patterns'] = {
            'typical_positions': {
                'beginning': sum(1 for p in flavor_positions if p < 0.3) / len(flavor_positions) if flavor_positions else 0,
                'middle': sum(1 for p in flavor_positions if 0.3 <= p < 0.7) / len(flavor_positions) if flavor_positions else 0,
                'end': sum(1 for p in flavor_positions if p >= 0.7) / len(flavor_positions) if flavor_positions else 0
            },
            'common_context_words': [word for word, count in flavor_keywords.most_common(30)]
        }
        
        self.stats['patterns_learned'] = len(flavor_keywords)
        
        print(f"  ✓ Изучено паттернов: {self.stats['patterns_learned']}")
        print(f"\n  📋 Структура названий (xname):")
        print(f"    Со скобками: {xname_patterns['has_parentheses']:5d} ({self.knowledge_base['xname_structure']['parentheses_ratio']*100:5.1f}%)")
        print(f"    С двоеточием: {xname_patterns['has_colon']:5d} ({self.knowledge_base['xname_structure']['colon_ratio']*100:5.1f}%)")
        print(f"    С объемом: {xname_patterns['has_volume']:5d} ({self.knowledge_base['xname_structure']['volume_ratio']*100:5.1f}%)")
        print(f"    С упаковкой: {xname_patterns['has_packaging']:5d} ({self.knowledge_base['xname_structure']['packaging_ratio']*100:5.1f}%)")
        print(f"\n  📍 Позиция брендов в названии:")
        print(f"    В начале: {self.knowledge_base['brand_patterns']['typical_positions']['beginning']*100:.1f}%")
        print(f"    В середине: {self.knowledge_base['brand_patterns']['typical_positions']['middle']*100:.1f}%")
        print(f"    В конце: {self.knowledge_base['brand_patterns']['typical_positions']['end']*100:.1f}%")
    
    def _learn_packaging(self, df: pd.DataFrame):
        """Обучение на типах упаковки"""
        packaging_types = Counter()
        
        for _, row in df.iterrows():
            pack = str(row.get('pack', '')).strip()
            if pack and pack != 'nan':
                packaging_types[pack] += 1
        
        self.knowledge_base['packaging_types'] = {
            pack: count for pack, count in packaging_types.items()
        }
        
        print(f"  Изучено типов упаковки: {len(packaging_types)}")
        for pack, count in packaging_types.most_common():
            print(f"    {pack}: {count} товаров")
    
    def _save_knowledge_base(self):
        """Сохранение базы знаний в JSON"""
        with open(self.knowledge_base_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
        
        print(f"  База знаний сохранена в: {self.knowledge_base_path}")
        
        # Сохраняем также базы из других компонентов
        self.brand_matcher.save_brands_db()
        print(f"  База брендов сохранена в: {self.brands_db_path}")
    
    def _print_statistics(self):
        """Вывод статистики обучения"""
        print("\n" + "="*80)
        print("СТАТИСТИКА ОБУЧЕНИЯ")
        print("="*80)
        print(f"Всего обработано товаров: {self.stats['total_products']}")
        print(f"Изучено брендов: {self.stats['brands_learned']}")
        print(f"Изучено вкусов: {self.stats['flavors_learned']}")
        print(f"Изучено категорий: {self.stats['categories_learned']}")
        print(f"Изучено паттернов: {self.stats['patterns_learned']}")
        print("="*80 + "\n")


class ModelValidator:
    """Валидатор модели - проверка качества распознавания"""
    
    def __init__(self, learning_engine: LearningEngine):
        self.engine = learning_engine
    
    def validate(self, df: pd.DataFrame, sample_size: int = 1000) -> Dict:
        """Валидация модели на выборке данных"""
        print("\n" + "="*80)
        print("ВАЛИДАЦИЯ МОДЕЛИ")
        print("="*80 + "\n")
        
        # Берем случайную выборку
        sample = df.sample(min(sample_size, len(df)))
        
        results = {
            'total': len(sample),
            'brand_correct': 0,
            'brand_partial': 0,
            'brand_wrong': 0,
            'volume_correct': 0,
            'packaging_correct': 0
        }
        
        for _, row in sample.iterrows():
            xname = str(row.get('xname', ''))
            actual_brand = str(row.get('brand', '')).strip().upper()
            actual_volume = row.get('litrag', None)
            actual_pack = str(row.get('pack', '')).strip().upper()
            
            # Парсим название
            features = self.engine.parser.parse(xname)
            
            # Пытаемся найти бренд
            brand_match = self.engine.brand_matcher.match_brand(
                xname, 
                list(self.engine.brand_matcher.brands_db.get('brands', {}).keys())
            )
            
            # Проверяем бренд
            if brand_match and actual_brand != 'LOCAL' and actual_brand != 'nan':
                if brand_match.matched_brand.upper() == actual_brand:
                    results['brand_correct'] += 1
                elif brand_match.confidence >= 75:
                    results['brand_partial'] += 1
                else:
                    results['brand_wrong'] += 1
            
            # Проверяем объем
            if features.volume and actual_volume:
                if abs(features.volume - float(actual_volume)) < 0.01:
                    results['volume_correct'] += 1
            
            # Проверяем упаковку
            if features.packaging and actual_pack != 'nan':
                if features.packaging == actual_pack:
                    results['packaging_correct'] += 1
        
        # Вычисляем точность
        total_brands = results['brand_correct'] + results['brand_partial'] + results['brand_wrong']
        
        print(f"Результаты валидации на {results['total']} товарах:")
        print(f"\nТочность распознавания брендов:")
        if total_brands > 0:
            print(f"  Точно: {results['brand_correct']} ({results['brand_correct']/total_brands*100:.1f}%)")
            print(f"  Частично: {results['brand_partial']} ({results['brand_partial']/total_brands*100:.1f}%)")
            print(f"  Неверно: {results['brand_wrong']} ({results['brand_wrong']/total_brands*100:.1f}%)")
        
        print(f"\nТочность распознавания объемов: {results['volume_correct']/results['total']*100:.1f}%")
        print(f"Точность распознавания упаковки: {results['packaging_correct']/results['total']*100:.1f}%")
        print("="*80 + "\n")
        
        return results


if __name__ == "__main__":
    # Обучение системы
    engine = LearningEngine(
        product_file='/workspace/product1.xlsx',
        sku_file='/workspace/sku_vkus.xlsx',
        knowledge_base_path='/workspace/knowledge_base.json',
        brands_db_path='/workspace/brands_db.json'
    )
    
    # Запуск обучения
    knowledge_base = engine.learn_from_data()
    
    # Валидация
    product_df, _ = engine.load_data()
    validator = ModelValidator(engine)
    validation_results = validator.validate(product_df, sample_size=500)
