#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенный скрипт запуска системы автоматической категоризации
"""

import os
import sys
import argparse


def print_header():
    """Вывод заголовка"""
    print("\n" + "="*80)
    print("  СИСТЕМА АВТОМАТИЧЕСКОЙ КАТЕГОРИЗАЦИИ ТОВАРОВ")
    print("  Версия 1.0.0")
    print("="*80 + "\n")


def check_files():
    """Проверка наличия необходимых файлов"""
    required_files = {
        'product1.xlsx': 'Файл с товарами',
        'sku_vkus.xlsx': 'Файл с вкусами'
    }
    
    missing = []
    for file, description in required_files.items():
        if not os.path.exists(file):
            missing.append(f"  - {file} ({description})")
    
    if missing:
        print("⚠️  ВНИМАНИЕ: Не найдены файлы:")
        for item in missing:
            print(item)
        print("\nПоложите файлы product1.xlsx и sku_vkus.xlsx в текущую папку.")
        return False
    
    print("✓ Все необходимые файлы найдены")
    return True


def check_knowledge_base():
    """Проверка наличия базы знаний"""
    if os.path.exists('knowledge_base.json') and os.path.exists('brands_db.json'):
        print("✓ База знаний найдена")
        return True
    else:
        print("⚠️  База знаний не найдена")
        return False


def run_demo():
    """Запуск демонстрации"""
    print("\n" + "-"*80)
    print("  РЕЖИМ ДЕМОНСТРАЦИИ")
    print("-"*80 + "\n")
    os.system('python3 demo.py')


def run_training():
    """Запуск обучения"""
    print("\n" + "-"*80)
    print("  ОБУЧЕНИЕ СИСТЕМЫ")
    print("-"*80 + "\n")
    print("Это займет 2-5 минут, подождите...\n")
    os.system('python3 learning_engine.py')


def run_categorization(input_file):
    """Запуск категоризации"""
    print("\n" + "-"*80)
    print("  КАТЕГОРИЗАЦИЯ ТОВАРОВ")
    print("-"*80 + "\n")
    
    if not os.path.exists(input_file):
        print(f"❌ ОШИБКА: Файл {input_file} не найден!")
        return
    
    cmd = f'python3 auto_categorizer.py -i {input_file} -p product1.xlsx -s sku_vkus.xlsx'
    os.system(cmd)


def interactive_mode():
    """Интерактивный режим"""
    print_header()
    
    print("Выберите действие:\n")
    print("1. Демонстрация возможностей (быстро)")
    print("2. Обучение системы (2-5 минут)")
    print("3. Категоризация товаров")
    print("4. Полный цикл (обучение + категоризация)")
    print("0. Выход\n")
    
    choice = input("Ваш выбор (0-4): ").strip()
    
    if choice == '1':
        run_demo()
    
    elif choice == '2':
        if not check_files():
            return
        run_training()
    
    elif choice == '3':
        if not check_files():
            return
        
        if not check_knowledge_base():
            print("\n⚠️  Сначала нужно обучить систему!")
            answer = input("Запустить обучение? (y/n): ").strip().lower()
            if answer == 'y':
                run_training()
            else:
                return
        
        input_file = input("\nВведите путь к файлу с товарами (по умолчанию: example_input.csv): ").strip()
        if not input_file:
            input_file = 'example_input.csv'
        
        run_categorization(input_file)
    
    elif choice == '4':
        if not check_files():
            return
        
        input_file = input("\nВведите путь к файлу с товарами (по умолчанию: example_input.csv): ").strip()
        if not input_file:
            input_file = 'example_input.csv'
        
        run_training()
        run_categorization(input_file)
    
    elif choice == '0':
        print("\nДо свидания!\n")
        return
    
    else:
        print("\n❌ Неверный выбор!")
    
    print("\n" + "="*80)
    print("  ГОТОВО!")
    print("="*80 + "\n")


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description='Система автоматической категоризации товаров',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Интерактивный режим
  python3 run.py

  # Демонстрация
  python3 run.py --demo

  # Обучение
  python3 run.py --train

  # Категоризация
  python3 run.py --categorize input.csv

  # Полный цикл
  python3 run.py --train --categorize input.csv
        """
    )
    
    parser.add_argument('--demo', action='store_true', help='Запустить демонстрацию')
    parser.add_argument('--train', action='store_true', help='Обучить систему')
    parser.add_argument('--categorize', metavar='FILE', help='Категоризировать товары из файла')
    
    args = parser.parse_args()
    
    # Если нет аргументов - интерактивный режим
    if not any(vars(args).values()):
        interactive_mode()
        return
    
    # Обработка аргументов командной строки
    print_header()
    
    if args.demo:
        run_demo()
    
    if args.train:
        if not check_files():
            return
        run_training()
    
    if args.categorize:
        if not check_files():
            return
        
        if not check_knowledge_base() and not args.train:
            print("\n⚠️  ВНИМАНИЕ: База знаний не найдена!")
            print("Запустите сначала обучение: python3 run.py --train")
            return
        
        run_categorization(args.categorize)
    
    print("\n" + "="*80)
    print("  ГОТОВО!")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}\n")
        sys.exit(1)
