#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Универсальный менеджер запуска BI системы
Позволяет выбрать между интерактивным дашбордом и HTML отчетом
"""

import os
import sys
import subprocess

def print_header():
    """Печатает заголовок"""
    print("="*80)
    print(" " * 25 + "BI СИСТЕМА - МЕНЕДЖЕР ЗАПУСКА")
    print("="*80)
    print()

def check_dependencies():
    """Проверяет установленные зависимости"""
    required = {
        'pandas': 'Работа с данными',
        'openpyxl': 'Чтение Excel файлов',
        'plotly': 'Построение графиков',
        'dash': 'Интерактивный дашборд',
        'numpy': 'Числовые вычисления'
    }
    
    print("🔍 Проверка зависимостей...")
    print()
    
    missing = []
    for package, description in required.items():
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package:20} - {description}")
        except ImportError:
            print(f"  ❌ {package:20} - {description} (НЕ УСТАНОВЛЕН)")
            missing.append(package)
    
    print()
    
    if missing:
        print(f"⚠️  Не хватает пакетов: {', '.join(missing)}")
        print()
        response = input("Установить недостающие пакеты? (y/n): ").lower()
        if response == 'y':
            print("\n📦 Установка пакетов...")
            try:
                for package in missing:
                    print(f"   Устанавливаю {package}...")
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install", package, "-q"
                    ])
                print("\n✅ Все пакеты установлены!")
                return True
            except Exception as e:
                print(f"\n❌ Ошибка при установке: {e}")
                return False
        else:
            return False
    else:
        print("✅ Все зависимости установлены!")
        return True

def find_data_file():
    """Ищет файл data.xlsx"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    possible_paths = [
        r'\\FS\Users\Private\GFD\Public\Трейд-маркетинг\7.Общие документы\Гусев\итог\data.xlsx',
        os.path.join(script_dir, 'data.xlsx'),
        'data.xlsx',
        os.environ.get('DATA_FILE_PATH', '')
    ]
    
    for path in possible_paths:
        if path and os.path.exists(path):
            return path
    
    return None

def main():
    """Основная функция"""
    print_header()
    
    # Проверка зависимостей
    if not check_dependencies():
        print("\n⚠️  Для продолжения необходимо установить зависимости.")
        input("\nНажмите Enter для выхода...")
        return
    
    print()
    print("="*80)
    print()
    
    # Поиск файла данных
    print("📂 Поиск файла данных...")
    data_file = find_data_file()
    
    if data_file:
        print(f"✅ Найден: {data_file}")
    else:
        print("❌ Файл data.xlsx не найден!")
        print("\n📂 Возможные решения:")
        print("   1. Скопируйте data.xlsx в папку с этим скриптом")
        print("   2. Установите переменную окружения DATA_FILE_PATH")
        print("   3. Измените путь в коде")
        input("\nНажмите Enter для выхода...")
        return
    
    # Установка переменной окружения
    os.environ['DATA_FILE_PATH'] = data_file
    
    print()
    print("="*80)
    print()
    print("Выберите режим работы:")
    print()
    print("  1️⃣  Интерактивный дашборд (Dash)")
    print("      - Запускает веб-сервер на http://localhost:8050")
    print("      - Интерактивные графики с фильтрами")
    print("      - Требует открытый браузер")
    print("      - Для остановки: Ctrl+C")
    print()
    print("  2️⃣  Статический HTML отчет")
    print("      - Создает один HTML файл")
    print("      - Можно открыть в любое время")
    print("      - Не требует запуска сервера")
    print("      - Легко отправить по email")
    print()
    print("  3️⃣  Оба варианта (сначала HTML, потом дашборд)")
    print()
    print("  0️⃣  Выход")
    print()
    print("="*80)
    
    choice = input("\nВаш выбор (1/2/3/0): ").strip()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    if choice == '1':
        # Запуск дашборда
        print("\n" + "="*80)
        print("🚀 Запуск интерактивного дашборда...")
        print("="*80)
        print("\n📊 После запуска откройте: http://localhost:8050")
        print("💡 Для остановки нажмите Ctrl+C\n")
        
        dashboard_path = os.path.join(script_dir, 'bi_dashboard.py')
        if os.path.exists(dashboard_path):
            try:
                subprocess.run([sys.executable, dashboard_path])
            except KeyboardInterrupt:
                print("\n\n⛔ Дашборд остановлен")
        else:
            print(f"❌ Файл не найден: {dashboard_path}")
    
    elif choice == '2':
        # Генерация HTML отчета
        print("\n" + "="*80)
        print("📊 Генерация HTML отчета...")
        print("="*80)
        
        report_path = os.path.join(script_dir, 'generate_html_report.py')
        if os.path.exists(report_path):
            try:
                subprocess.run([sys.executable, report_path])
                
                # Предложить открыть отчет
                html_file = os.path.join(script_dir, 'bi_report.html')
                if os.path.exists(html_file):
                    print("\n" + "="*80)
                    response = input("Открыть отчет в браузере? (y/n): ").lower()
                    if response == 'y':
                        import webbrowser
                        webbrowser.open('file://' + os.path.abspath(html_file))
                        print("✅ Отчет открыт в браузере!")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
        else:
            print(f"❌ Файл не найден: {report_path}")
    
    elif choice == '3':
        # Оба варианта
        print("\n" + "="*80)
        print("📊 Генерация HTML отчета...")
        print("="*80)
        
        report_path = os.path.join(script_dir, 'generate_html_report.py')
        if os.path.exists(report_path):
            subprocess.run([sys.executable, report_path])
        
        print("\n" + "="*80)
        print("🚀 Запуск интерактивного дашборда...")
        print("="*80)
        print("\n📊 После запуска откройте: http://localhost:8050")
        print("💡 Для остановки нажмите Ctrl+C\n")
        
        dashboard_path = os.path.join(script_dir, 'bi_dashboard.py')
        if os.path.exists(dashboard_path):
            try:
                subprocess.run([sys.executable, dashboard_path])
            except KeyboardInterrupt:
                print("\n\n⛔ Дашборд остановлен")
    
    elif choice == '0':
        print("\n👋 До свидания!")
        return
    
    else:
        print("\n❌ Неверный выбор!")
    
    print("\n" + "="*80)
    input("\nНажмите Enter для выхода...")

if __name__ == '__main__':
    main()
