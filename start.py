#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ГЛАВНЫЙ ФАЙЛ ЗАПУСКА СИСТЕМЫ
Используйте этот файл для работы с системой!
"""

import os
import sys

# Импортируем настройки
from settings import (
    FOLDER_PATH, PRODUCT_FILE, SKU_FILE, INPUT_FILE,
    OUTPUT_PRODUCT_FILE, OUTPUT_SKU_FILE,
    KNOWLEDGE_BASE_FILE, BRANDS_DB_FILE,
    validate_settings, print_settings
)


def print_header():
    """Вывод заголовка"""
    print("\n" + "="*80)
    print("  🤖 СИСТЕМА АВТОМАТИЧЕСКОЙ КАТЕГОРИЗАЦИИ ТОВАРОВ")
    print("  Версия 1.0.0")
    print("="*80 + "\n")


def show_menu():
    """Главное меню"""
    print("Выберите действие:\n")
    print("1. 📋 Показать текущие настройки")
    print("2. 🎯 Демонстрация возможностей")
    print("3. 🎓 Обучить систему на данных")
    print("4. 🚀 Обработать новые товары")
    print("5. 🔄 Полный цикл (обучение + обработка)")
    print("6. ⚙️  Изменить настройки (settings.py)")
    print("0. ❌ Выход\n")


def run_demo():
    """Демонстрация"""
    print("\n" + "-"*80)
    print("  ДЕМОНСТРАЦИЯ ВОЗМОЖНОСТЕЙ")
    print("-"*80 + "\n")
    os.system('python3 demo.py')


def run_training():
    """Обучение"""
    print("\n" + "-"*80)
    print("  ОБУЧЕНИЕ СИСТЕМЫ")
    print("-"*80 + "\n")
    
    if not os.path.exists(PRODUCT_FILE) or not os.path.exists(SKU_FILE):
        print("❌ ОШИБКА: Не найдены файлы для обучения!")
        print("\n💡 Откройте settings.py и укажите правильные пути")
        return
    
    print("📚 Обучение на данных из:")
    print(f"   {PRODUCT_FILE}")
    print(f"   {SKU_FILE}")
    print("\n⏳ Это займет 2-5 минут, подождите...\n")
    
    cmd = f'python3 learning_engine.py'
    
    # Создаем символические ссылки если файлы в другой папке
    if FOLDER_PATH != os.getcwd():
        if not os.path.exists('product1.xlsx'):
            os.symlink(PRODUCT_FILE, 'product1.xlsx')
        if not os.path.exists('sku_vkus.xlsx'):
            os.symlink(SKU_FILE, 'sku_vkus.xlsx')
    
    os.system(cmd)


def run_categorization():
    """Категоризация"""
    print("\n" + "-"*80)
    print("  ОБРАБОТКА НОВЫХ ТОВАРОВ")
    print("-"*80 + "\n")
    
    # Проверяем наличие базы знаний
    if not os.path.exists(KNOWLEDGE_BASE_FILE) or not os.path.exists(BRANDS_DB_FILE):
        print("⚠️  База знаний не найдена!")
        answer = input("Запустить обучение? (y/n): ").strip().lower()
        if answer == 'y':
            run_training()
        else:
            return
    
    # Проверяем входной файл
    input_file = INPUT_FILE
    if not os.path.exists(input_file):
        print(f"⚠️  Входной файл не найден: {input_file}")
        print("\nВведите путь к файлу с новыми товарами:")
        custom_input = input("Путь: ").strip()
        if custom_input:
            input_file = custom_input
            if not os.path.exists(input_file):
                print(f"❌ ОШИБКА: Файл {input_file} не найден!")
                return
        else:
            print("❌ Файл не указан")
            return
    
    print(f"📥 Обработка файла: {input_file}")
    print(f"📊 Используются данные из:")
    print(f"   {PRODUCT_FILE}")
    print(f"   {SKU_FILE}")
    print()
    
    cmd = f'python3 auto_categorizer.py -i "{input_file}" -p "{PRODUCT_FILE}" -s "{SKU_FILE}" -op "{OUTPUT_PRODUCT_FILE}" -os "{OUTPUT_SKU_FILE}"'
    os.system(cmd)


def run_full_cycle():
    """Полный цикл"""
    print("\n" + "-"*80)
    print("  ПОЛНЫЙ ЦИКЛ (ОБУЧЕНИЕ + ОБРАБОТКА)")
    print("-"*80 + "\n")
    
    # Проверяем входной файл
    input_file = INPUT_FILE
    if not os.path.exists(input_file):
        print(f"⚠️  Входной файл не найден: {input_file}")
        print("\nВведите путь к файлу с новыми товарами:")
        custom_input = input("Путь: ").strip()
        if custom_input:
            input_file = custom_input
            if not os.path.exists(input_file):
                print(f"❌ ОШИБКА: Файл {input_file} не найден!")
                return
        else:
            print("❌ Файл не указан")
            return
    
    print(f"📥 Будет обработан: {input_file}\n")
    
    cmd = f'python3 auto_categorizer.py -i "{input_file}" -p "{PRODUCT_FILE}" -s "{SKU_FILE}" -op "{OUTPUT_PRODUCT_FILE}" -os "{OUTPUT_SKU_FILE}" --train'
    os.system(cmd)


def edit_settings():
    """Редактирование настроек"""
    print("\n" + "-"*80)
    print("  РЕДАКТИРОВАНИЕ НАСТРОЕК")
    print("-"*80 + "\n")
    
    print("📝 Откройте файл: settings.py")
    print("\n💡 В нем вы можете изменить:")
    print("   - FOLDER_PATH    (путь к папке с файлами)")
    print("   - PRODUCT_FILE   (файл с товарами)")
    print("   - SKU_FILE       (файл с вкусами)")
    print("   - INPUT_FILE     (входной файл)")
    print("   - и другие настройки...")
    
    print("\n📖 Пример:")
    print('   FOLDER_PATH = "/home/user/documents/products"')
    
    print("\n" + "-"*80)
    answer = input("\nОткрыть файл в редакторе? (y/n): ").strip().lower()
    
    if answer == 'y':
        # Пытаемся открыть в разных редакторах
        editors = ['nano', 'vim', 'vi', 'gedit', 'kate', 'code', 'notepad']
        for editor in editors:
            if os.system(f'which {editor} > /dev/null 2>&1') == 0:
                os.system(f'{editor} settings.py')
                break
        else:
            print(f"\n📁 Откройте файл вручную: {os.path.abspath('settings.py')}")


def main():
    """Главная функция"""
    print_header()
    
    # Проверяем настройки
    if not validate_settings():
        print("\n💡 Сначала настройте пути к файлам в settings.py")
        print("   Запустите: python3 settings.py")
        return
    
    while True:
        show_menu()
        choice = input("Ваш выбор (0-6): ").strip()
        
        if choice == '1':
            print_settings()
        
        elif choice == '2':
            run_demo()
        
        elif choice == '3':
            run_training()
        
        elif choice == '4':
            run_categorization()
        
        elif choice == '5':
            run_full_cycle()
        
        elif choice == '6':
            edit_settings()
        
        elif choice == '0':
            print("\n👋 До свидания!\n")
            break
        
        else:
            print("\n❌ Неверный выбор!")
        
        input("\nНажмите Enter для продолжения...")
        print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
