#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт проверки совместимости системы с BI Dashboard
Запустите перед установкой для проверки вашей системы
"""

import sys
import platform

def print_header(text):
    """Красивый заголовок"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def check_python_version():
    """Проверка версии Python"""
    print_header("🐍 ПРОВЕРКА PYTHON")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print(f"Версия Python: {version_str}")
    print(f"Платформа: {platform.platform()}")
    print(f"Архитектура: {platform.machine()}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ ВНИМАНИЕ: Требуется Python 3.8 или выше!")
        print("   Скачайте с https://www.python.org/downloads/")
        return False
    elif version.minor >= 13:
        print("✅ Отлично! У вас самая новая версия Python")
        return True
    elif version.minor >= 9:
        print("✅ Хорошо! Версия Python подходит")
        return True
    else:
        print("⚠️  Версия Python подходит, но рекомендуется 3.9+")
        return True

def check_package(name, display_name=None):
    """Проверка установленного пакета"""
    if display_name is None:
        display_name = name
    
    try:
        module = __import__(name.replace('-', '_'))
        version = getattr(module, '__version__', 'неизвестна')
        print(f"✅ {display_name:30} {version}")
        return True, version
    except ImportError:
        print(f"❌ {display_name:30} НЕ УСТАНОВЛЕН")
        return False, None

def check_dash_api():
    """Специальная проверка API Dash"""
    try:
        from dash import Dash
        app = Dash(__name__)
        
        if hasattr(app, 'run'):
            print("   ✅ Dash 2.0+ API (app.run) - СОВМЕСТИМО")
            return True
        elif hasattr(app, 'run_server'):
            print("   ⚠️  Старый Dash API (app.run_server) - ТРЕБУЕТСЯ ОБНОВЛЕНИЕ")
            print("      Обновите: pip install --upgrade dash")
            return False
        else:
            print("   ❓ Не удалось определить версию API")
            return None
    except ImportError:
        return None

def main():
    """Основная функция"""
    print("="*80)
    print(" "*25 + "ПРОВЕРКА СОВМЕСТИМОСТИ")
    print(" "*28 + "BI Dashboard v1.0")
    print("="*80)
    
    # Проверка Python
    python_ok = check_python_version()
    
    # Проверка пакетов
    print_header("📦 ПРОВЕРКА БИБЛИОТЕК")
    
    required_packages = [
        ('pandas', 'Pandas (обработка данных)'),
        ('openpyxl', 'OpenPyXL (чтение Excel)'),
        ('plotly', 'Plotly (графики)'),
        ('dash', 'Dash (веб-фреймворк)'),
        ('dash_bootstrap_components', 'Dash Bootstrap Components'),
        ('numpy', 'NumPy (вычисления)')
    ]
    
    results = {}
    missing = []
    
    for package, display_name in required_packages:
        installed, version = check_package(package, display_name)
        results[package] = (installed, version)
        if not installed:
            missing.append(package)
    
    # Специальная проверка Dash API
    if results['dash'][0]:
        print("\n🔍 Проверка Dash API:")
        dash_api_ok = check_dash_api()
    
    # Итоги
    print_header("📊 ИТОГИ")
    
    all_ok = python_ok and len(missing) == 0
    
    if all_ok:
        print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print("\n🎉 Ваша система полностью совместима с BI Dashboard")
        print("   Вы можете запускать дашборд прямо сейчас!")
        print("\n📝 Следующие шаги:")
        print("   1. Запустите: python bi_dashboard.py")
        print("   2. Откройте: http://localhost:8050")
    else:
        print("⚠️  ОБНАРУЖЕНЫ ПРОБЛЕМЫ")
        
        if not python_ok:
            print("\n❌ Python:")
            print("   Требуется Python 3.8 или выше")
            print("   Скачайте: https://www.python.org/downloads/")
        
        if missing:
            print(f"\n❌ Недостающие библиотеки ({len(missing)}):")
            for package in missing:
                print(f"   - {package}")
            
            print("\n💡 Установите командой:")
            print("   pip install " + " ".join(missing))
            print("\n   Или все сразу:")
            print("   pip install pandas openpyxl plotly dash dash-bootstrap-components numpy")
    
    # Рекомендации
    print_header("💡 РЕКОМЕНДАЦИИ")
    
    if results.get('dash', (False, None))[0]:
        dash_version = results['dash'][1]
        try:
            major, minor = dash_version.split('.')[:2]
            if int(major) >= 2:
                print("✅ Dash: версия актуальная")
            else:
                print("⚠️  Dash: рекомендуется обновить до версии 2.0+")
                print("   pip install --upgrade dash")
        except:
            pass
    
    if results.get('pandas', (False, None))[0]:
        pandas_version = results['pandas'][1]
        try:
            major = int(pandas_version.split('.')[0])
            if major >= 2:
                print("✅ Pandas: версия актуальная")
            else:
                print("⚠️  Pandas: рекомендуется обновить до версии 2.0+")
                print("   pip install --upgrade pandas")
        except:
            pass
    
    # Дополнительная информация
    print_header("📚 ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ")
    print("Документация:")
    print("  • START_HERE.md - начните с этого файла")
    print("  • QUICK_START.txt - быстрый старт (5 минут)")
    print("  • VERSION_NOTES.md - заметки о версиях")
    print("  • CHECKLIST.md - пошаговый чек-лист")
    print("\nПоддержка:")
    print("  • GitHub: https://github.com/did2210/cursor.git")
    print("  • Документация: README.md")
    
    print("\n" + "="*80)
    
    if all_ok:
        print("🚀 Готово! Можно запускать дашборд!")
    else:
        print("🔧 Установите недостающие компоненты и запустите проверку снова")
    
    print("="*80)
    
    return all_ok

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⛔ Проверка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Ошибка при проверке: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
