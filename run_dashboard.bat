@echo off
chcp 65001 >nul
echo ================================================================================
echo 🚀 BI DASHBOARD - ЗАПУСК
echo ================================================================================
echo.

REM Путь к вашему файлу данных (измените если нужно)
set DATA_FILE_PATH=\\FS\Users\Private\GFD\Public\Трейд-маркетинг\7.Общие документы\Гусев\итог\data.xlsx

REM Если файл в той же папке, раскомментируйте следующую строку:
REM set DATA_FILE_PATH=%~dp0data.xlsx

echo 📂 Путь к данным: %DATA_FILE_PATH%
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo.
    echo 💡 Установите Python с https://www.python.org/downloads/
    echo    При установке обязательно отметьте "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo ✅ Python найден
echo.

REM Проверка и установка библиотек
echo 📦 Проверка необходимых библиотек...
echo.

python -c "import pandas" >nul 2>&1
if errorlevel 1 (
    echo 📥 Установка pandas...
    pip install pandas openpyxl -q
)

python -c "import plotly" >nul 2>&1
if errorlevel 1 (
    echo 📥 Установка plotly...
    pip install plotly -q
)

python -c "import dash" >nul 2>&1
if errorlevel 1 (
    echo 📥 Установка dash...
    pip install dash dash-bootstrap-components -q
)

python -c "import numpy" >nul 2>&1
if errorlevel 1 (
    echo 📥 Установка numpy...
    pip install numpy -q
)

echo.
echo ✅ Все библиотеки установлены!
echo.
echo ================================================================================
echo 🎯 ЗАПУСК ДАШБОРДА...
echo ================================================================================
echo.
echo 📊 После запуска откройте браузер и перейдите по адресу:
echo    http://localhost:8050
echo.
echo 💡 Для остановки нажмите Ctrl+C
echo.
echo ================================================================================
echo.

REM Запуск дашборда
python "%~dp0bi_dashboard.py"

if errorlevel 1 (
    echo.
    echo ❌ Произошла ошибка при запуске!
    echo.
    pause
)
