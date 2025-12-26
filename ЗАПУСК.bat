@echo off
chcp 65001 >nul
color 0A
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║         🚀 ПРОФЕССИОНАЛЬНЫЙ BI DASHBOARD                    ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 📂 Проверка файлов...
if not exist "professional_bi_dashboard.py" (
    echo ❌ ОШИБКА: Файл professional_bi_dashboard.py не найден!
    pause
    exit
)
echo ✅ Файлы найдены
echo.
echo 🔧 Проверка зависимостей...
python -c "import dash" 2>nul
if errorlevel 1 (
    echo ⚠️  Dash не установлен. Устанавливаю...
    pip install dash dash-bootstrap-components plotly pandas openpyxl -q
)
echo ✅ Зависимости готовы
echo.
echo ════════════════════════════════════════════════════════════════
echo    🚀 ЗАПУСК СЕРВЕРА...
echo ════════════════════════════════════════════════════════════════
echo.
echo    📍 После запуска откройте: http://localhost:8050
echo    ⏹️  Для остановки нажмите: Ctrl+C
echo.
echo ════════════════════════════════════════════════════════════════
echo.
python professional_bi_dashboard.py
pause
