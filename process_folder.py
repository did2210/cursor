#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для обработки файлов из указанной папки
Автоматически ищет product1.xlsx и sku_vkus.xlsx в указанной папке
"""

import os
import sys
import argparse
from pathlib import Path


def find_files_in_folder(folder_path):
    """Поиск необходимых файлов в папке"""
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ ОШИБКА: Папка {folder_path} не существует!")
        return None, None, None
    
    # Ищем файлы
    product_file = None
    sku_file = None
    input_file = None
    
    # Поиск product файла
    for pattern in ['product*.xlsx', 'product*.xls', 'Product*.xlsx']:
        files = list(folder.glob(pattern))
        if files:
            product_file = str(files[0])
            break
    
    # Поиск sku файла
    for pattern in ['sku*.xlsx', 'sku*.xls', 'Sku*.xlsx', '*vkus*.xlsx']:
        files = list(folder.glob(pattern))
        if files:
            sku_file = str(files[0])
            break
    
    # Поиск входного файла (новые товары)
    for pattern in ['new*.csv', 'new*.xlsx', 'input*.csv', 'input*.xlsx', 'товар*.xlsx', 'товар*.csv']:
        files = list(folder.glob(pattern))
        if files:
            input_file = str(files[0])
            break
    
    return product_file, sku_file, input_file


def print_found_files(product_file, sku_file, input_file, folder_path):
    """Вывод найденных файлов"""
    print("\n" + "="*80)
    print(f"📁 ПАПКА: {folder_path}")
    print("="*80)
    
    print("\n✓ НАЙДЕННЫЕ ФАЙЛЫ:")
    
    if product_file:
        print(f"  📊 Файл с товарами: {os.path.basename(product_file)}")
    else:
        print(f"  ❌ Файл с товарами: НЕ НАЙДЕН")
    
    if sku_file:
        print(f"  📊 Файл с вкусами: {os.path.basename(sku_file)}")
    else:
        print(f"  ❌ Файл с вкусами: НЕ НАЙДЕН")
    
    if input_file:
        print(f"  📥 Входной файл: {os.path.basename(input_file)}")
    else:
        print(f"  ⚠️  Входной файл: НЕ НАЙДЕН (можно указать вручную)")
    
    print("="*80 + "\n")


def interactive_mode():
    """Интерактивный режим с выбором папки"""
    print("\n" + "="*80)
    print("  ОБРАБОТКА ФАЙЛОВ ИЗ ПАПКИ")
    print("="*80 + "\n")
    
    # Запрос пути к папке
    print("Введите путь к папке с файлами:")
    print("Примеры:")
    print("  /workspace")
    print("  /home/user/documents/products")
    print("  C:\\Users\\User\\Documents\\Products")
    print("  . (текущая папка)")
    print()
    
    folder_path = input("Путь к папке: ").strip()
    
    if not folder_path:
        folder_path = "."
    
    # Поиск файлов
    product_file, sku_file, input_file = find_files_in_folder(folder_path)
    
    # Вывод найденных файлов
    print_found_files(product_file, sku_file, input_file, folder_path)
    
    # Проверка обязательных файлов
    if not product_file or not sku_file:
        print("❌ ОШИБКА: Не найдены обязательные файлы!")
        print("\nВ папке должны быть:")
        print("  - product*.xlsx (или product1.xlsx)")
        print("  - sku*.xlsx (или sku_vkus.xlsx)")
        return
    
    # Если входной файл не найден, спросить у пользователя
    if not input_file:
        print("Введите имя входного файла с новыми товарами")
        print("(или нажмите Enter, чтобы создать пример):")
        input_filename = input("Имя файла: ").strip()
        
        if input_filename:
            input_file = os.path.join(folder_path, input_filename)
            if not os.path.exists(input_file):
                print(f"❌ ОШИБКА: Файл {input_file} не найден!")
                return
        else:
            print("\n⚠️  Входной файл не указан. Создайте файл с новыми товарами.")
            return
    
    # Выбор действия
    print("Что делать дальше?\n")
    print("1. Только обучить систему")
    print("2. Обучить и обработать новые товары")
    print("3. Только обработать новые товары (если уже обучена)")
    print("0. Отмена\n")
    
    choice = input("Ваш выбор (0-3): ").strip()
    
    if choice == '1':
        # Только обучение
        cmd = f'python3 learning_engine.py'
        print(f"\n🔄 Запуск обучения...\n")
        
        # Временно меняем рабочую директорию
        original_dir = os.getcwd()
        os.chdir(folder_path)
        os.system(cmd)
        os.chdir(original_dir)
    
    elif choice == '2':
        # Обучение + обработка
        print(f"\n🔄 Запуск полного цикла...\n")
        
        cmd = f'python3 auto_categorizer.py -i "{input_file}" -p "{product_file}" -s "{sku_file}" --train'
        os.system(cmd)
    
    elif choice == '3':
        # Только обработка
        print(f"\n🔄 Запуск обработки...\n")
        
        cmd = f'python3 auto_categorizer.py -i "{input_file}" -p "{product_file}" -s "{sku_file}"'
        os.system(cmd)
    
    elif choice == '0':
        print("\n❌ Отменено\n")
        return
    
    else:
        print("\n❌ Неверный выбор!\n")
        return
    
    print("\n" + "="*80)
    print("  ✓ ГОТОВО!")
    print("="*80)
    print(f"\nРезультаты сохранены в папке: {folder_path}")
    print("  - product1_updated.xlsx")
    print("  - sku_vkus_updated.xlsx\n")


def command_line_mode(args):
    """Режим командной строки"""
    folder_path = args.folder
    
    # Поиск файлов
    product_file, sku_file, input_file = find_files_in_folder(folder_path)
    
    # Вывод найденных файлов
    print_found_files(product_file, sku_file, input_file, folder_path)
    
    # Проверка обязательных файлов
    if not product_file or not sku_file:
        print("❌ ОШИБКА: Не найдены обязательные файлы!")
        sys.exit(1)
    
    # Если входной файл указан явно
    if args.input:
        input_file = args.input
        if not os.path.isabs(input_file):
            input_file = os.path.join(folder_path, input_file)
    
    if not input_file:
        print("❌ ОШИБКА: Не указан входной файл с новыми товарами!")
        print("Используйте параметр --input или положите файл new*.csv в папку")
        sys.exit(1)
    
    # Запуск обработки
    print(f"🔄 Обработка файлов...\n")
    
    train_flag = '--train' if args.train else ''
    cmd = f'python3 auto_categorizer.py -i "{input_file}" -p "{product_file}" -s "{sku_file}" {train_flag}'
    
    os.system(cmd)
    
    print("\n" + "="*80)
    print("  ✓ ГОТОВО!")
    print("="*80)


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description='Обработка файлов из указанной папки',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Интерактивный режим (с выбором папки)
  python3 process_folder.py

  # Указать папку в командной строке
  python3 process_folder.py --folder /path/to/folder

  # Указать папку и входной файл
  python3 process_folder.py --folder /path/to/folder --input new_products.csv

  # С обучением
  python3 process_folder.py --folder /path/to/folder --input new_products.csv --train

Скрипт автоматически найдет в папке:
  - product*.xlsx (файл с товарами)
  - sku*.xlsx (файл с вкусами)
  - new*.csv или input*.csv (входной файл, опционально)
        """
    )
    
    parser.add_argument('--folder', '-f', help='Путь к папке с файлами')
    parser.add_argument('--input', '-i', help='Имя входного файла с новыми товарами')
    parser.add_argument('--train', '-t', action='store_true', help='Обучить систему перед обработкой')
    
    args = parser.parse_args()
    
    try:
        if args.folder:
            # Режим командной строки
            command_line_mode(args)
        else:
            # Интерактивный режим
            interactive_mode()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
