#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой лаунчер для BI Dashboard
Просто запустите этот файл!
"""

import os
import sys
import subprocess

def check_and_install_packages():
    """Проверяет и устанавливает необходимые пакеты"""
    required_packages = [
        'pandas',
        'openpyxl',
        'plotly',
        'dash',
        'dash-bootstrap-components',
        'numpy'
    ]
    
    print("🔍 Проверка установленных пакетов...")
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} установлен")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} не найден")
    
    if missing_packages:
        print(f"\n📦 Установка недостающих пакетов: {', '.join(missing_packages)}")
        for package in missing_packages:
            print(f"\nУстанавливаем {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])
        print("\n✅ Все пакеты установлены!")
    else:
        print("\n✅ Все необходимые пакеты уже установлены!")

def main():
    """Основная функция запуска"""
    print("="*80)
    print("🚀 BI DASHBOARD LAUNCHER")
    print("="*80)
    
    # Проверка и установка пакетов
    try:
        check_and_install_packages()
    except Exception as e:
        print(f"\n❌ Ошибка при установке пакетов: {e}")
        print("\n💡 Попробуйте вручную установить:")
        print("pip install pandas openpyxl plotly dash dash-bootstrap-components numpy")
        input("\nНажмите Enter для выхода...")
        return
    
    print("\n" + "="*80)
    
    # Определяем пути к файлам
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dashboard_path = os.path.join(script_dir, 'bi_dashboard.py')
    
    # Варианты путей к data.xlsx
    possible_data_paths = [
        # Путь пользователя
        r'\\FS\Users\Private\GFD\Public\Трейд-маркетинг\7.Общие документы\Гусев\итог\data.xlsx',
        # В той же папке что и скрипты
        os.path.join(script_dir, 'data.xlsx'),
        # Другие возможные варианты
        'data.xlsx'
    ]
    
    data_file = None
    for path in possible_data_paths:
        if os.path.exists(path):
            data_file = path
            print(f"✅ Найден файл данных: {path}")
            break
    
    if not data_file:
        print("❌ Файл data.xlsx не найден!")
        print("\n📂 Проверьте следующие пути:")
        for path in possible_data_paths:
            print(f"   - {path}")
        print("\n💡 Положите файл data.xlsx рядом с этим скриптом или укажите правильный путь")
        input("\nНажмите Enter для выхода...")
        return
    
    if not os.path.exists(dashboard_path):
        print(f"❌ Файл bi_dashboard.py не найден по пути: {dashboard_path}")
        print("\n💡 Убедитесь, что файлы run_dashboard.py и bi_dashboard.py находятся в одной папке")
        input("\nНажмите Enter для выхода...")
        return
    
    # Запуск дашборда
    print("\n" + "="*80)
    print("🎯 Запуск BI Dashboard...")
    print("="*80)
    print("\n📊 После запуска откройте в браузере: http://localhost:8050")
    print("\n💡 Для остановки закройте это окно или нажмите Ctrl+C")
    print("\n" + "="*80 + "\n")
    
    try:
        # Создаем временную переменную окружения с путем к данным
        env = os.environ.copy()
        env['DATA_FILE_PATH'] = data_file
        
        # Запускаем дашборд
        subprocess.run([sys.executable, dashboard_path], env=env)
    except KeyboardInterrupt:
        print("\n\n⛔ Дашборд остановлен пользователем")
    except Exception as e:
        print(f"\n\n❌ Ошибка при запуске: {e}")
        input("\nНажмите Enter для выхода...")

if __name__ == '__main__':
    main()
