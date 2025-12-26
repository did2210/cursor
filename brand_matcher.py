#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для нечеткого сопоставления брендов с поддержкой транслитерации
и различных написаний (сокращений, ошибок и т.д.)
"""

import re
from typing import List, Tuple, Dict, Optional
from rapidfuzz import fuzz, process
from dataclasses import dataclass
import json


# Словарь транслитерации русский -> латиница
TRANSLIT_RU_TO_EN = {
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
    'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
    'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
    'Ф': 'F', 'Х': 'H', 'Ц': 'TS', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SCH',
    'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'YU', 'Я': 'YA'
}

# Словарь транслитерации латиница -> русский
TRANSLIT_EN_TO_RU = {
    'A': 'А', 'B': 'Б', 'C': 'К', 'D': 'Д', 'E': 'Е', 'F': 'Ф',
    'G': 'Г', 'H': 'Х', 'I': 'И', 'J': 'ДЖ', 'K': 'К', 'L': 'Л',
    'M': 'М', 'N': 'Н', 'O': 'О', 'P': 'П', 'Q': 'К', 'R': 'Р',
    'S': 'С', 'T': 'Т', 'U': 'У', 'V': 'В', 'W': 'В', 'X': 'КС',
    'Y': 'Й', 'Z': 'З'
}


@dataclass
class BrandMatch:
    """Результат сопоставления бренда"""
    original: str
    matched_brand: str
    confidence: float
    method: str  # exact, fuzzy, translit, abbreviated
    variations: List[str] = None
    
    def __post_init__(self):
        if self.variations is None:
            self.variations = []


class BrandMatcher:
    """Класс для нечеткого сопоставления брендов"""
    
    def __init__(self, brands_db_path: str = None):
        self.brands_db_path = brands_db_path
        self.brands_db = self._load_brands_db()
        
        # Пороги для нечеткого сопоставления
        self.exact_threshold = 100
        self.high_confidence_threshold = 90
        self.medium_confidence_threshold = 75
        self.low_confidence_threshold = 60
        
    def get_all_brands(self) -> List[str]:
        """Получить список всех известных брендов"""
        return list(self.brands_db.get('brands', {}).keys())
        
    def _load_brands_db(self) -> Dict:
        """Загрузка базы данных брендов"""
        if self.brands_db_path:
            try:
                with open(self.brands_db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except FileNotFoundError:
                return {'brands': {}, 'aliases': {}}
        return {'brands': {}, 'aliases': {}}
    
    def save_brands_db(self):
        """Сохранение базы данных брендов"""
        if self.brands_db_path:
            with open(self.brands_db_path, 'w', encoding='utf-8') as f:
                json.dump(self.brands_db, f, ensure_ascii=False, indent=2)
    
    def transliterate_ru_to_en(self, text: str) -> str:
        """Транслитерация с русского на английский"""
        result = []
        i = 0
        text_upper = text.upper()
        
        while i < len(text_upper):
            # Проверяем двухбуквенные комбинации
            if i < len(text_upper) - 1:
                two_char = text_upper[i:i+2]
                if two_char in ['Ж', 'Ц', 'Ч', 'Ш', 'Щ', 'Ю', 'Я']:
                    result.append(TRANSLIT_RU_TO_EN.get(two_char[0], two_char[0]))
                    i += 1
                    continue
            
            # Одиночный символ
            char = text_upper[i]
            result.append(TRANSLIT_RU_TO_EN.get(char, char))
            i += 1
        
        return ''.join(result)
    
    def transliterate_en_to_ru(self, text: str) -> str:
        """Транслитерация с английского на русский"""
        result = []
        text_upper = text.upper()
        
        for char in text_upper:
            result.append(TRANSLIT_EN_TO_RU.get(char, char))
        
        return ''.join(result)
    
    def generate_variations(self, brand: str) -> List[str]:
        """Генерация вариаций написания бренда"""
        variations = [brand.upper()]
        
        # Добавляем транслитерации
        variations.append(self.transliterate_ru_to_en(brand))
        variations.append(self.transliterate_en_to_ru(brand))
        
        # Добавляем сокращения (первые 4-6 символов)
        if len(brand) > 4:
            variations.append(brand[:4].upper())
            variations.append(brand[:5].upper())
            variations.append(brand[:6].upper())
        
        # Убираем дубликаты
        variations = list(set(variations))
        
        return variations
    
    def add_brand_to_db(self, brand: str, aliases: List[str] = None):
        """Добавление бренда в базу данных"""
        brand_upper = brand.upper()
        
        if brand_upper not in self.brands_db['brands']:
            self.brands_db['brands'][brand_upper] = {
                'canonical': brand_upper,
                'variations': self.generate_variations(brand),
                'aliases': aliases or []
            }
        
        # Добавляем алиасы
        if aliases:
            for alias in aliases:
                alias_upper = alias.upper()
                self.brands_db['aliases'][alias_upper] = brand_upper
        
        self.save_brands_db()
    
    def match_brand(self, text: str, known_brands: List[str]) -> Optional[BrandMatch]:
        """
        Сопоставление текста с известными брендами
        
        Args:
            text: текст для поиска бренда
            known_brands: список известных брендов
            
        Returns:
            BrandMatch или None
        """
        text_upper = text.upper()
        
        # 1. Точное совпадение
        for brand in known_brands:
            brand_upper = brand.upper()
            if brand_upper in text_upper:
                return BrandMatch(
                    original=text,
                    matched_brand=brand,
                    confidence=100.0,
                    method='exact'
                )
        
        # 2. Поиск по алиасам
        for alias, canonical in self.brands_db.get('aliases', {}).items():
            if alias in text_upper:
                return BrandMatch(
                    original=text,
                    matched_brand=canonical,
                    confidence=95.0,
                    method='alias'
                )
        
        # 3. Поиск с транслитерацией
        text_translit_en = self.transliterate_ru_to_en(text_upper)
        text_translit_ru = self.transliterate_en_to_ru(text_upper)
        
        for brand in known_brands:
            brand_upper = brand.upper()
            brand_translit_en = self.transliterate_ru_to_en(brand_upper)
            brand_translit_ru = self.transliterate_en_to_ru(brand_upper)
            
            if brand_translit_en in text_translit_en or brand_translit_ru in text_translit_ru:
                return BrandMatch(
                    original=text,
                    matched_brand=brand,
                    confidence=90.0,
                    method='translit'
                )
        
        # 4. Нечеткое сопоставление
        # Разбиваем текст на слова
        words = re.findall(r'\b[А-ЯA-Z][А-ЯA-Z0-9]*\b', text_upper)
        
        best_match = None
        best_score = 0
        
        for word in words:
            # Пропускаем общие слова
            if word in ['НАПИТОК', 'ВОДА', 'СОК', 'НЕКТАР', 'МОРС', 'КВАС']:
                continue
            
            # Нечеткое сравнение
            for brand in known_brands:
                brand_upper = brand.upper()
                
                # Используем несколько методов сравнения
                ratio = fuzz.ratio(word, brand_upper)
                partial_ratio = fuzz.partial_ratio(word, brand_upper)
                token_sort_ratio = fuzz.token_sort_ratio(word, brand_upper)
                
                # Берем максимальный скор
                score = max(ratio, partial_ratio, token_sort_ratio)
                
                if score > best_score:
                    best_score = score
                    best_match = brand
        
        # Если нашли достаточно хорошее совпадение
        if best_score >= self.low_confidence_threshold:
            method = 'fuzzy_high' if best_score >= self.high_confidence_threshold else 'fuzzy_medium'
            return BrandMatch(
                original=text,
                matched_brand=best_match,
                confidence=best_score,
                method=method
            )
        
        # 5. Поиск сокращений
        for brand in known_brands:
            brand_upper = brand.upper()
            # Проверяем, является ли какое-то слово началом бренда
            for word in words:
                if len(word) >= 3 and brand_upper.startswith(word):
                    return BrandMatch(
                        original=text,
                        matched_brand=brand,
                        confidence=80.0,
                        method='abbreviated'
                    )
        
        return None
    
    def match_from_text(self, text: str) -> Optional[BrandMatch]:
        """Сопоставление бренда из текста используя загруженную базу"""
        known_brands = list(self.brands_db.get('brands', {}).keys())
        return self.match_brand(text, known_brands)
    
    def learn_brand_variation(self, text: str, correct_brand: str):
        """Обучение на примере - добавление вариации бренда"""
        brand_upper = correct_brand.upper()
        text_upper = text.upper()
        
        # Инициализируем бренд если его нет
        if brand_upper not in self.brands_db['brands']:
            self.add_brand_to_db(correct_brand)
        
        # Добавляем вариацию
        if text_upper not in self.brands_db['brands'][brand_upper]['variations']:
            self.brands_db['brands'][brand_upper]['variations'].append(text_upper)
        
        self.save_brands_db()


class FlavorMatcher:
    """Класс для сопоставления вкусов с поддержкой нечеткого поиска"""
    
    def __init__(self, flavors_db_path: str = None):
        self.flavors_db_path = flavors_db_path
        self.flavors_db = self._load_flavors_db()
    
    def _load_flavors_db(self) -> Dict:
        """Загрузка базы вкусов из JSON"""
        if self.flavors_db_path:
            try:
                with open(self.flavors_db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('flavors', {})
            except FileNotFoundError:
                return {}
        return {}
    
    def add_flavor(self, flavor: str, aliases: List[str] = None):
        """Добавление вкуса в базу"""
        flavor_upper = flavor.upper()
        if flavor_upper not in self.flavors_db:
            self.flavors_db[flavor_upper] = aliases or []
    
    def save_flavors_db(self):
        """Сохранение базы вкусов"""
        if self.flavors_db_path:
            try:
                with open(self.flavors_db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = {}
            
            data['flavors'] = self.flavors_db
            
            with open(self.flavors_db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_all_flavors(self) -> List[str]:
        """Получить список всех известных вкусов"""
        return list(self.flavors_db.keys())
    
    def match_flavor(self, text: str) -> Optional[str]:
        """Сопоставление вкуса из текста"""
        text_upper = text.upper()
        
        # Точное совпадение
        for flavor, aliases in self.flavors_db.items():
            if flavor in text_upper:
                return flavor
            for alias in aliases:
                if alias in text_upper:
                    return flavor
        
        # Нечеткое совпадение
        words = re.findall(r'\b[А-ЯA-Z]{3,}\b', text_upper)
        
        for word in words:
            for flavor, aliases in self.flavors_db.items():
                # Проверяем сам вкус
                if fuzz.ratio(word, flavor) >= 85:
                    return flavor
                # Проверяем алиасы
                for alias in aliases:
                    if fuzz.ratio(word, alias) >= 85:
                        return flavor
        
        return None


if __name__ == "__main__":
    # Тестирование с реальными данными
    print("="*80)
    print("ТЕСТИРОВАНИЕ МОДУЛЯ BRAND_MATCHER")
    print("="*80)
    
    # Проверяем наличие обученной базы
    import os
    if not os.path.exists('brands_db.json'):
        print("\n⚠️  ВНИМАНИЕ: База брендов не найдена!")
        print("Сначала запустите обучение системы:")
        print("  python3 learning_engine.py")
        print("\nЗатем повторите тест.")
    else:
        # Загружаем обученную базу
        matcher = BrandMatcher('brands_db.json')
        flavor_matcher = FlavorMatcher('brands_db.json')
        
        brands = matcher.get_all_brands()
        flavors = flavor_matcher.get_all_flavors()
        
        print(f"\n✓ База брендов загружена")
        print(f"  Количество брендов: {len(brands)}")
        print(f"  Количество вкусов: {len(flavors)}")
        
        print(f"\n📊 Топ-10 брендов:")
        for i, brand in enumerate(sorted(brands)[:10], 1):
            print(f"  {i}. {brand}")
        
        print(f"\n🍎 Топ-10 вкусов:")
        for i, flavor in enumerate(sorted(flavors)[:10], 1):
            print(f"  {i}. {flavor}")
        
        # Тестирование на реальных примерах
        print(f"\n🧪 ТЕСТИРОВАНИЕ РАСПОЗНАВАНИЯ:\n")
        
        test_cases = [
            'Напиток ДОБРЫЙ КОЛА БЕЗ САХАРА ГАЗ. ПЭТ 2Л',
            'Минеральная вода ЧИСТОЗЕРЬЕ ГАЗ. ПЭТ 0,5Л',
            'ФРУКТОВЫЙ САД НЕКТАР ЯБЛОЧНЫЙ ОСВЕТЛ 1,93Л',
        ]
        
        for test in test_cases:
            print(f"Текст: '{test}'")
            result = matcher.match_brand(test, brands[:100])  # Первые 100 брендов
            if result:
                print(f"  ✓ Бренд: {result.matched_brand} ({result.confidence:.1f}%, метод: {result.method})")
            else:
                print(f"  ❌ Бренд не найден")
            
            flavor = flavor_matcher.match_flavor(test)
            if flavor:
                print(f"  ✓ Вкус: {flavor}")
            print()
