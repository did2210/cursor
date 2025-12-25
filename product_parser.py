#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для парсинга названий товаров и извлечения признаков
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json


@dataclass
class ProductFeatures:
    """Извлеченные признаки из названия товара"""
    original_name: str
    brand: Optional[str] = None
    product_type: Optional[str] = None
    volume: Optional[float] = None
    volume_unit: Optional[str] = None
    flavor: Optional[str] = None
    packaging: Optional[str] = None
    carbonation: Optional[str] = None  # ГАЗ/БЕЗ ГАЗА
    sugar_free: bool = False
    attributes: List[str] = None
    confidence: float = 0.0
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = []


class ProductNameParser:
    """Парсер названий товаров с извлечением признаков"""
    
    def __init__(self, knowledge_base_path: str = None):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = self._load_knowledge_base()
        
        # Паттерны для распознавания
        self.volume_patterns = [
            r'(\d+[,.]?\d*)\s*[ЛL]',  # 0,5Л или 0.5L
            r'(\d+)\s*[МM][ЛL]',       # 500МЛ
        ]
        
        self.packaging_keywords = {
            'ПЭТ': 'PET',
            'PET': 'PET',
            'Ж/Б': 'CAN',  # Жестяная банка
            'Ж.Б': 'CAN',
            'ЖБ': 'CAN',
            'СТЕКЛО': 'GLASS',
            'БАНКА': 'CAN',
            'CAN': 'CAN',
            'БУТЫЛКА': 'BOTTLE',
            'BOTTLE': 'BOTTLE',
            'ЖЕСТЬ': 'CAN',
            'АЛЮМИНИЙ': 'CAN',
            'ТЕТРАПАК': 'TETRA',
            'TETRAPAK': 'TETRA'
        }
        
        self.carbonation_keywords = {
            'ГАЗ': 'carbonated',
            'ГАЗИРОВАННАЯ': 'carbonated',
            'ГАЗИРОВАННЫЙ': 'carbonated',
            'БЕЗ ГАЗА': 'non_carbonated',
            'НЕГАЗИРОВАННАЯ': 'non_carbonated',
            'НЕГАЗИРОВАННЫЙ': 'non_carbonated',
        }
        
        self.product_types = {
            'ВОДА': 'water',
            'НАПИТОК': 'beverage',
            'СОК': 'juice',
            'НЕКТАР': 'nectar',
            'МОРС': 'mors',
            'КВАС': 'kvass',
            'КОЛА': 'cola',
            'ЛИМОНАД': 'lemonade',
            'ЭНЕРГЕТИК': 'energy_drink',
            'ЧАЙ': 'tea',
            'КОФЕ': 'coffee',
        }
        
        self.sugar_keywords = [
            'БЕЗ САХАРА',
            'ZERO',
            'ЗЕРО',
            'LIGHT',
            'ЛАЙТ',
            'SUGAR FREE'
        ]
        
    def _load_knowledge_base(self) -> Dict:
        """Загрузка базы знаний из JSON"""
        if self.knowledge_base_path:
            try:
                with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except FileNotFoundError:
                return self._create_default_knowledge_base()
        return self._create_default_knowledge_base()
    
    def _create_default_knowledge_base(self) -> Dict:
        """Создание базовой базы знаний"""
        return {
            'brands': {},
            'flavors': {},
            'patterns': {},
            'aliases': {}
        }
    
    def save_knowledge_base(self):
        """Сохранение базы знаний"""
        if self.knowledge_base_path:
            with open(self.knowledge_base_path, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
    
    def parse(self, product_name: str) -> ProductFeatures:
        """Парсинг названия товара и извлечение признаков"""
        features = ProductFeatures(original_name=product_name)
        
        # Нормализация названия
        normalized = product_name.upper().strip()
        
        # Извлечение объема
        features.volume, features.volume_unit = self._extract_volume(normalized)
        
        # Извлечение типа упаковки
        features.packaging = self._extract_packaging(normalized)
        
        # Извлечение газированности
        features.carbonation = self._extract_carbonation(normalized)
        
        # Проверка на отсутствие сахара
        features.sugar_free = self._check_sugar_free(normalized)
        
        # Извлечение типа продукта
        features.product_type = self._extract_product_type(normalized)
        
        # Извлечение бренда (самая сложная часть)
        features.brand = self._extract_brand(normalized)
        
        # Извлечение вкуса
        features.flavor = self._extract_flavor(normalized)
        
        # Извлечение дополнительных атрибутов
        features.attributes = self._extract_attributes(normalized)
        
        return features
    
    def _extract_volume(self, text: str) -> Tuple[Optional[float], Optional[str]]:
        """Извлечение объема"""
        for pattern in self.volume_patterns:
            match = re.search(pattern, text)
            if match:
                volume_str = match.group(1).replace(',', '.')
                try:
                    volume = float(volume_str)
                    return volume, 'L'
                except ValueError:
                    continue
        return None, None
    
    def _extract_packaging(self, text: str) -> Optional[str]:
        """Извлечение типа упаковки"""
        for keyword, pack_type in self.packaging_keywords.items():
            if keyword in text:
                return pack_type
        return None
    
    def _extract_carbonation(self, text: str) -> Optional[str]:
        """Извлечение информации о газированности"""
        for keyword, carb_type in self.carbonation_keywords.items():
            if keyword in text:
                return carb_type
        return None
    
    def _check_sugar_free(self, text: str) -> bool:
        """Проверка на отсутствие сахара"""
        for keyword in self.sugar_keywords:
            if keyword in text:
                return True
        return False
    
    def _extract_product_type(self, text: str) -> Optional[str]:
        """Извлечение типа продукта"""
        for keyword, prod_type in self.product_types.items():
            if keyword in text:
                return prod_type
        return None
    
    def _extract_brand(self, text: str) -> Optional[str]:
        """Извлечение бренда (базовая версия, улучшается в brand_matcher.py)"""
        # Обычно бренд идет в начале или указан в скобках
        # Пример: "ФРУСТИНО НАПИТОК..." -> ФРУСТИНО
        # Пример: "...0,5Л(ВЭЗН):20" -> ВЭЗН
        # Пример: "Напиток ДОБРЫЙ КОЛА..." -> ДОБРЫЙ
        
        # Поиск в скобках (производитель)
        bracket_match = re.search(r'\(([^)]+)\)', text)
        if bracket_match:
            potential_brand = bracket_match.group(1).strip()
            # Убираем служебные слова
            if potential_brand and not any(x in potential_brand for x in [':', ';', 'ООО', 'ОАО']):
                return potential_brand
        
        # Убираем префиксы типа "Энергетический напиток", "Минеральная вода" и т.д.
        text_cleaned = text
        prefixes_to_remove = [
            'ЭНЕРГЕТИЧЕСКИЙ НАПИТОК',
            'МИНЕРАЛЬНАЯ ВОДА',
            'НАПИТОК',
            'ВОДА',
            'СОК',
            'НЕКТАР',
            'МОРС',
            'КВАС'
        ]
        
        for prefix in prefixes_to_remove:
            if text_cleaned.startswith(prefix):
                text_cleaned = text_cleaned[len(prefix):].strip()
                break
        
        # Берем первое слово после удаления префикса
        words = text_cleaned.split()
        if words:
            first_word = words[0].strip()
            # Исключаем общие слова и артикли
            if first_word and len(first_word) > 1:
                return first_word
        
        # Если ничего не нашли, берем первое слово оригинального текста
        words = text.split()
        if words:
            first_word = words[0].strip()
            if first_word not in ['НАПИТОК', 'ВОДА', 'СОК', 'НЕКТАР', 'МОРС', 'КВАС']:
                return first_word
        
        return None
    
    def _extract_flavor(self, text: str) -> Optional[str]:
        """Извлечение вкуса"""
        # Список популярных вкусов
        flavors = [
            'ЯБЛОКО', 'АПЕЛЬСИН', 'ЛИМОН', 'ВИШНЯ', 'ПЕРСИК', 'ГРУША',
            'ДЮШЕС', 'КЛУБНИКА', 'МАЛИНА', 'СМОРОДИНА', 'ВИНОГРАД',
            'КОЛА', 'ТАРХУН', 'БУРАТИНО', 'БАЙКАЛ', 'САЯНЫ',
            'АНАНАС', 'МАНГО', 'МАНДАРИН', 'ГРЕЙПФРУТ', 'БАНАН',
            'ТОМАТ', 'ТОМАТНЫЙ', 'МУЛЬТИФРУКТ', 'ТРОПИК'
        ]
        
        for flavor in flavors:
            if flavor in text:
                return flavor
        
        return None
    
    def _extract_attributes(self, text: str) -> List[str]:
        """Извлечение дополнительных атрибутов"""
        attributes = []
        
        attribute_keywords = {
            'ОСВЕТЛ': 'clarified',
            'С МЯКОТЬЮ': 'with_pulp',
            'С МЯК': 'with_pulp',
            'БЕЗ МЯКОТИ': 'no_pulp',
            'Б/А': 'non_alcoholic',
            'БЕЗАЛКОГОЛЬНЫЙ': 'non_alcoholic',
            'НАТУРАЛЬНЫЙ': 'natural',
            'МИНЕРАЛЬНАЯ': 'mineral',
            'ПИТЬЕВАЯ': 'drinking',
            'СТОЛОВАЯ': 'table',
            'ЛЕЧЕБНАЯ': 'therapeutic',
        }
        
        for keyword, attr in attribute_keywords.items():
            if keyword in text:
                attributes.append(attr)
        
        return attributes
    
    def learn_from_example(self, product_name: str, correct_features: Dict):
        """Обучение на примере (добавление в базу знаний)"""
        normalized = product_name.upper().strip()
        
        # Добавляем бренд в базу знаний
        if 'brand' in correct_features:
            brand = correct_features['brand']
            if brand not in self.knowledge_base['brands']:
                self.knowledge_base['brands'][brand] = []
            
            # Добавляем паттерны бренда
            if normalized not in self.knowledge_base['brands'][brand]:
                self.knowledge_base['brands'][brand].append(normalized)
        
        # Добавляем вкусы
        if 'flavor' in correct_features:
            flavor = correct_features['flavor']
            if flavor not in self.knowledge_base['flavors']:
                self.knowledge_base['flavors'][flavor] = []
            
            if normalized not in self.knowledge_base['flavors'][flavor]:
                self.knowledge_base['flavors'][flavor].append(normalized)
        
        # Сохраняем обновленную базу знаний
        self.save_knowledge_base()


if __name__ == "__main__":
    # Тестирование парсера
    parser = ProductNameParser()
    
    test_cases = [
        "Минеральная вода ЧИСТОЗЕРЬЕ ГАЗ. ПЭТ 0,5Л",
        "Напиток ДОБРЫЙ КОЛА БЕЗ САХАРА ГАЗ. ПЭТ 2Л",
        "ФРУСТИНО НАПИТОК Б/А ДЮШЕС 0,5Л(ВЭЗН):20",
        "КРАСАВЧИК НЕКТАР ЯБЛОКО 0,95Л(САНФРУТ-ТРЕЙД):12"
    ]
    
    for test in test_cases:
        print(f"\nОригинал: {test}")
        features = parser.parse(test)
        print(f"Результат парсинга:")
        print(f"  Бренд: {features.brand}")
        print(f"  Тип: {features.product_type}")
        print(f"  Объем: {features.volume} {features.volume_unit}")
        print(f"  Упаковка: {features.packaging}")
        print(f"  Газирование: {features.carbonation}")
        print(f"  Без сахара: {features.sugar_free}")
        print(f"  Вкус: {features.flavor}")
        print(f"  Атрибуты: {features.attributes}")
