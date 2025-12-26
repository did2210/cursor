@echo off
chcp 65001 >nul
color 0B

echo.
echo ══════════════════════════════════════════════════════════════════
echo              🧪 ТЕСТ И ЗАПУСК BI DASHBOARD
echo ══════════════════════════════════════════════════════════════════
echo.

rem Проверка Python
echo [1/4] Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не установлен или не в PATH
    echo 💡 Установите Python с https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python найден

rem Проверка библиотек
echo.
echo [2/4] Проверка библиотек...
python -c "import dash" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Dash не установлен. Устанавливаю...
    pip install dash dash-bootstrap-components plotly pandas openpyxl -q
    if errorlevel 1 (
        echo ❌ Ошибка установки
        pause
        exit /b 1
    )
    echo ✅ Библиотеки установлены
) else (
    echo ✅ Все библиотеки на месте
)

rem Проверка файла данных
echo.
echo [3/4] Проверка файла данных...
if exist "data.xlsx" (
    echo ✅ Файл data.xlsx найден
) else (
    echo.
    echo ══════════════════════════════════════════════════════════════════
    echo ❌ ОШИБКА: Файл data.xlsx не найден!
    echo ══════════════════════════════════════════════════════════════════
    echo.
    echo 💡 Что нужно сделать:
    echo.
    echo    1. Поместите файл data.xlsx в эту же папку где скрипты
    echo.
    echo    2. ИЛИ откройте professional_bi_dashboard.py
    echo       и укажите полный путь к файлу в строке DATA_PATH
    echo.
    echo Текущая папка: %CD%
    echo.
    pause
    exit /b 1
)

rem Проверка скрипта
echo.
echo [4/4] Проверка скрипта...
if not exist "professional_bi_dashboard.py" (
    echo ❌ Файл professional_bi_dashboard.py не найден
    pause
    exit /b 1
)
echo ✅ Скрипт найден

echo.
echo ══════════════════════════════════════════════════════════════════
echo              ✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ
echo ══════════════════════════════════════════════════════════════════
echo.
echo 🚀 Запускаю сервер...
echo.
echo ══════════════════════════════════════════════════════════════════
echo    📍 После запуска откройте: http://localhost:8050
echo    ⏹️  Для остановки нажмите: Ctrl+C
echo ══════════════════════════════════════════════════════════════════
echo.

python professional_bi_dashboard.py
pause
