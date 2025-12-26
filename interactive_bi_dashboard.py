"""
Интерактивный BI Dashboard с фильтрами
Создает standalone HTML файл с полной интерактивностью
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime

print("="*80)
print("         🎯 СОЗДАНИЕ ИНТЕРАКТИВНОГО BI ДАШБОРДА")
print("="*80)

# Загрузка данных
print("\n📂 Загрузка данных...")
df = pd.read_excel('/workspace/data.xlsx')

# Подготовка данных
df['Дата'] = pd.to_datetime(df['Дата'])
df['Месяц_название'] = df['Дата'].dt.strftime('%Y-%m')
df['Месяц_для_сортировки'] = df['Дата'].dt.strftime('%Y-%m')

# Заполнение пропущенных значений
numeric_cols = df.select_dtypes(include=[np.number]).columns
df[numeric_cols] = df[numeric_cols].fillna(0)

print(f"✅ Загружено {len(df):,} записей")
print(f"📅 Период: {df['Дата'].min().date()} → {df['Дата'].max().date()}")

# Подготовка данных для JavaScript
print("\n🔧 Подготовка данных для интерактивного дашборда...")

# Создаем структуру данных
data_records = df.to_dict('records')

# Преобразуем даты в строки для JSON
for record in data_records:
    if pd.notna(record.get('Дата')):
        record['Дата'] = record['Дата'].strftime('%Y-%m-%d')
    if pd.notna(record.get('начало_контракта')):
        record['начало_контракта'] = record['начало_контракта'].strftime('%Y-%m-%d')
    if pd.notna(record.get('конец_контракта')):
        record['конец_контракта'] = record['конец_контракта'].strftime('%Y-%m-%d')

# Получаем уникальные значения для фильтров
contracts = sorted(df['Контракт'].unique().tolist())
networks = sorted(df['Сеть'].unique().tolist())
brands = sorted(df['Brand_format'].unique().tolist())
groups = sorted(df['группа сбыта'].unique().tolist())

print(f"✅ Контрактов: {len(contracts)}")
print(f"✅ Сетей: {len(networks)}")
print(f"✅ Брендов: {len(brands)}")

# Создаем HTML с встроенным JavaScript
html_content = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 Интерактивный BI Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        
        .container {{
            max-width: 1800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 36px;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .filters {{
            background: #f8f9fa;
            padding: 25px 30px;
            border-bottom: 3px solid #667eea;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }}
        
        .filter-group {{
            display: flex;
            flex-direction: column;
        }}
        
        .filter-group label {{
            font-weight: 600;
            margin-bottom: 8px;
            color: #2c3e50;
            font-size: 14px;
        }}
        
        .filter-group select {{
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            background: white;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .filter-group select:hover {{
            border-color: #667eea;
        }}
        
        .filter-group select:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        
        .reset-btn {{
            padding: 12px 24px;
            background: #e74c3c;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            align-self: flex-end;
        }}
        
        .reset-btn:hover {{
            background: #c0392b;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        .kpi-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .kpi-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-left: 5px solid;
            transition: all 0.3s;
        }}
        
        .kpi-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }}
        
        .kpi-card.blue {{ border-color: #3498db; }}
        .kpi-card.green {{ border-color: #2ecc71; }}
        .kpi-card.orange {{ border-color: #e67e22; }}
        .kpi-card.purple {{ border-color: #9b59b6; }}
        .kpi-card.red {{ border-color: #e74c3c; }}
        .kpi-card.teal {{ border-color: #1abc9c; }}
        
        .kpi-label {{
            font-size: 13px;
            color: #7f8c8d;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .kpi-value {{
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .kpi-subvalue {{
            font-size: 14px;
            color: #7f8c8d;
            margin-top: 5px;
        }}
        
        .charts-container {{
            padding: 30px;
        }}
        
        .chart-wrapper {{
            background: white;
            margin-bottom: 30px;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .chart-title {{
            font-size: 20px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        .loading {{
            text-align: center;
            padding: 40px;
            font-size: 18px;
            color: #7f8c8d;
        }}
        
        .no-data {{
            text-align: center;
            padding: 40px;
            font-size: 18px;
            color: #e74c3c;
            background: #fee;
            border-radius: 8px;
            margin: 20px;
        }}
        
        .info-banner {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            margin: 30px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        
        .info-banner .text {{
            font-size: 16px;
        }}
        
        .info-banner .count {{
            font-size: 24px;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Интерактивный BI Dashboard</h1>
            <p>Анализ продаж и затрат с возможностью фильтрации</p>
        </div>
        
        <div class="filters">
            <div class="filter-group">
                <label>📋 Контракт</label>
                <select id="contractFilter">
                    <option value="">Все контракты ({len(contracts)})</option>
                </select>
            </div>
            
            <div class="filter-group">
                <label>🏪 Сеть</label>
                <select id="networkFilter">
                    <option value="">Все сети ({len(networks)})</option>
                </select>
            </div>
            
            <div class="filter-group">
                <label>🎯 Бренд</label>
                <select id="brandFilter">
                    <option value="">Все бренды ({len(brands)})</option>
                </select>
            </div>
            
            <div class="filter-group">
                <label>📊 Группа сбыта</label>
                <select id="groupFilter">
                    <option value="">Все группы</option>
                </select>
            </div>
            
            <div class="filter-group">
                <label>&nbsp;</label>
                <button class="reset-btn" onclick="resetFilters()">🔄 Сбросить фильтры</button>
            </div>
        </div>
        
        <div class="info-banner">
            <div>
                <div class="text">📊 Отображаемых записей:</div>
                <div class="count" id="recordCount">{len(df):,}</div>
            </div>
            <div>
                <div class="text">📅 Период данных:</div>
                <div class="count" id="datePeriod">{df['Дата'].min().strftime('%Y-%m')} - {df['Дата'].max().strftime('%Y-%m')}</div>
            </div>
        </div>
        
        <div class="kpi-container" id="kpiContainer">
            <div class="kpi-card blue">
                <div class="kpi-label">💰 Продажи План</div>
                <div class="kpi-value" id="kpi-plan-sales">-</div>
                <div class="kpi-subvalue">млрд руб</div>
            </div>
            
            <div class="kpi-card green">
                <div class="kpi-label">✅ Продажи Факт</div>
                <div class="kpi-value" id="kpi-fact-sales">-</div>
                <div class="kpi-subvalue">млрд руб</div>
            </div>
            
            <div class="kpi-card purple">
                <div class="kpi-label">📈 Выполнение плана</div>
                <div class="kpi-value" id="kpi-fulfillment">-</div>
                <div class="kpi-subvalue">процентов</div>
            </div>
            
            <div class="kpi-card orange">
                <div class="kpi-label">💸 Затраты</div>
                <div class="kpi-value" id="kpi-costs">-</div>
                <div class="kpi-subvalue">млрд руб</div>
            </div>
            
            <div class="kpi-card teal">
                <div class="kpi-label">💎 Доход</div>
                <div class="kpi-value" id="kpi-income">-</div>
                <div class="kpi-subvalue">млрд руб</div>
            </div>
            
            <div class="kpi-card red">
                <div class="kpi-label">🎯 ROI</div>
                <div class="kpi-value" id="kpi-roi">-</div>
                <div class="kpi-subvalue">процентов</div>
            </div>
        </div>
        
        <div class="charts-container">
            <div class="chart-wrapper">
                <div class="chart-title">📊 Продажи: План vs Факт по месяцам</div>
                <div id="salesChart"></div>
            </div>
            
            <div class="chart-wrapper">
                <div class="chart-title">📈 Выполнение плана по месяцам</div>
                <div id="fulfillmentChart"></div>
            </div>
            
            <div class="chart-wrapper">
                <div class="chart-title">💰 Финансовые показатели</div>
                <div id="financialChart"></div>
            </div>
            
            <div class="chart-wrapper">
                <div class="chart-title">🎯 ROI по месяцам</div>
                <div id="roiChart"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Данные
        const allData = {json.dumps(data_records, ensure_ascii=False)};
        const contracts = {json.dumps(contracts, ensure_ascii=False)};
        const networks = {json.dumps(networks, ensure_ascii=False)};
        const brands = {json.dumps(brands, ensure_ascii=False)};
        const groups = {json.dumps(groups, ensure_ascii=False)};
        
        let currentData = allData;
        
        // Инициализация фильтров
        function initFilters() {{
            const contractFilter = document.getElementById('contractFilter');
            const networkFilter = document.getElementById('networkFilter');
            const brandFilter = document.getElementById('brandFilter');
            const groupFilter = document.getElementById('groupFilter');
            
            contracts.forEach(item => {{
                const option = document.createElement('option');
                option.value = item;
                option.textContent = item;
                contractFilter.appendChild(option);
            }});
            
            networks.forEach(item => {{
                const option = document.createElement('option');
                option.value = item;
                option.textContent = item;
                networkFilter.appendChild(option);
            }});
            
            brands.forEach(item => {{
                const option = document.createElement('option');
                option.value = item;
                option.textContent = item;
                brandFilter.appendChild(option);
            }});
            
            groups.forEach(item => {{
                const option = document.createElement('option');
                option.value = item;
                option.textContent = item;
                groupFilter.appendChild(option);
            }});
            
            // Добавляем обработчики событий
            contractFilter.addEventListener('change', applyFilters);
            networkFilter.addEventListener('change', applyFilters);
            brandFilter.addEventListener('change', applyFilters);
            groupFilter.addEventListener('change', applyFilters);
        }}
        
        // Применение фильтров
        function applyFilters() {{
            const contract = document.getElementById('contractFilter').value;
            const network = document.getElementById('networkFilter').value;
            const brand = document.getElementById('brandFilter').value;
            const group = document.getElementById('groupFilter').value;
            
            currentData = allData.filter(row => {{
                return (contract === '' || row['Контракт'] === contract) &&
                       (network === '' || row['Сеть'] === network) &&
                       (brand === '' || row['Brand_format'] === brand) &&
                       (group === '' || row['группа сбыта'] === group);
            }});
            
            document.getElementById('recordCount').textContent = currentData.length.toLocaleString('ru-RU');
            
            if (currentData.length === 0) {{
                showNoData();
            }} else {{
                updateDashboard();
            }}
        }}
        
        // Сброс фильтров
        function resetFilters() {{
            document.getElementById('contractFilter').value = '';
            document.getElementById('networkFilter').value = '';
            document.getElementById('brandFilter').value = '';
            document.getElementById('groupFilter').value = '';
            
            currentData = allData;
            document.getElementById('recordCount').textContent = allData.length.toLocaleString('ru-RU');
            updateDashboard();
        }}
        
        // Показать сообщение об отсутствии данных
        function showNoData() {{
            const message = '<div class="no-data">⚠️ Нет данных для выбранных фильтров. Попробуйте изменить критерии поиска.</div>';
            document.getElementById('salesChart').innerHTML = message;
            document.getElementById('fulfillmentChart').innerHTML = message;
            document.getElementById('financialChart').innerHTML = message;
            document.getElementById('roiChart').innerHTML = message;
            
            // Обнуляем KPI
            document.getElementById('kpi-plan-sales').textContent = '0';
            document.getElementById('kpi-fact-sales').textContent = '0';
            document.getElementById('kpi-fulfillment').textContent = '0';
            document.getElementById('kpi-costs').textContent = '0';
            document.getElementById('kpi-income').textContent = '0';
            document.getElementById('kpi-roi').textContent = '0';
        }}
        
        // Обновление дашборда
        function updateDashboard() {{
            updateKPIs();
            updateSalesChart();
            updateFulfillmentChart();
            updateFinancialChart();
            updateROIChart();
        }}
        
        // Обновление KPI
        function updateKPIs() {{
            let planSales = 0, factSales = 0, costs = 0, income = 0;
            
            currentData.forEach(row => {{
                planSales += row['Плановые продажи, руб'] || 0;
                factSales += row['Факт продажи, руб (от ЦМ)'] || 0;
                costs += row['факт затраты'] || 0;
                income += row['доход факт'] || 0;
            }});
            
            const fulfillment = planSales > 0 ? (factSales / planSales * 100) : 0;
            const roi = costs > 0 ? (income / costs * 100) : 0;
            
            document.getElementById('kpi-plan-sales').textContent = (planSales / 1e9).toFixed(2);
            document.getElementById('kpi-fact-sales').textContent = (factSales / 1e9).toFixed(2);
            document.getElementById('kpi-fulfillment').textContent = fulfillment.toFixed(1) + '%';
            document.getElementById('kpi-costs').textContent = (costs / 1e9).toFixed(2);
            document.getElementById('kpi-income').textContent = (income / 1e9).toFixed(2);
            document.getElementById('kpi-roi').textContent = roi.toFixed(1) + '%';
        }}
        
        // График продаж
        function updateSalesChart() {{
            const monthlyData = {{}};
            
            currentData.forEach(row => {{
                const month = row['Месяц_название'];
                if (!monthlyData[month]) {{
                    monthlyData[month] = {{plan: 0, fact: 0}};
                }}
                monthlyData[month].plan += row['Плановые продажи, руб'] || 0;
                monthlyData[month].fact += row['Факт продажи, руб (от ЦМ)'] || 0;
            }});
            
            const months = Object.keys(monthlyData).sort();
            const planValues = months.map(m => monthlyData[m].plan / 1e9);
            const factValues = months.map(m => monthlyData[m].fact / 1e9);
            
            const trace1 = {{
                x: months,
                y: planValues,
                name: 'План',
                type: 'bar',
                marker: {{ color: '#3498db' }}
            }};
            
            const trace2 = {{
                x: months,
                y: factValues,
                name: 'Факт',
                type: 'bar',
                marker: {{ color: '#2ecc71' }}
            }};
            
            const layout = {{
                barmode: 'group',
                xaxis: {{ title: 'Месяц' }},
                yaxis: {{ title: 'Продажи, млрд руб' }},
                height: 400,
                margin: {{ l: 60, r: 30, t: 30, b: 80 }}
            }};
            
            Plotly.newPlot('salesChart', [trace1, trace2], layout, {{responsive: true}});
        }}
        
        // График выполнения плана
        function updateFulfillmentChart() {{
            const monthlyData = {{}};
            
            currentData.forEach(row => {{
                const month = row['Месяц_название'];
                if (!monthlyData[month]) {{
                    monthlyData[month] = {{plan: 0, fact: 0}};
                }}
                monthlyData[month].plan += row['Плановые продажи, руб'] || 0;
                monthlyData[month].fact += row['Факт продажи, руб (от ЦМ)'] || 0;
            }});
            
            const months = Object.keys(monthlyData).sort();
            const fulfillmentValues = months.map(m => 
                monthlyData[m].plan > 0 ? (monthlyData[m].fact / monthlyData[m].plan * 100) : 0
            );
            
            const trace = {{
                x: months,
                y: fulfillmentValues,
                type: 'scatter',
                mode: 'lines+markers',
                marker: {{ size: 10, color: '#9b59b6' }},
                line: {{ width: 3, color: '#9b59b6' }}
            }};
            
            const layout = {{
                xaxis: {{ title: 'Месяц' }},
                yaxis: {{ title: 'Выполнение, %' }},
                height: 400,
                margin: {{ l: 60, r: 30, t: 30, b: 80 }},
                shapes: [{{
                    type: 'line',
                    x0: months[0],
                    x1: months[months.length - 1],
                    y0: 100,
                    y1: 100,
                    line: {{ color: 'red', width: 2, dash: 'dash' }}
                }}]
            }};
            
            Plotly.newPlot('fulfillmentChart', [trace], layout, {{responsive: true}});
        }}
        
        // График финансовых показателей
        function updateFinancialChart() {{
            const monthlyData = {{}};
            
            currentData.forEach(row => {{
                const month = row['Месяц_название'];
                if (!monthlyData[month]) {{
                    monthlyData[month] = {{costs: 0, income: 0}};
                }}
                monthlyData[month].costs += row['факт затраты'] || 0;
                monthlyData[month].income += row['доход факт'] || 0;
            }});
            
            const months = Object.keys(monthlyData).sort();
            const costsValues = months.map(m => monthlyData[m].costs / 1e9);
            const incomeValues = months.map(m => monthlyData[m].income / 1e9);
            
            const trace1 = {{
                x: months,
                y: costsValues,
                name: 'Затраты',
                type: 'bar',
                marker: {{ color: '#e67e22' }}
            }};
            
            const trace2 = {{
                x: months,
                y: incomeValues,
                name: 'Доход',
                type: 'bar',
                marker: {{ color: '#1abc9c' }}
            }};
            
            const layout = {{
                barmode: 'group',
                xaxis: {{ title: 'Месяц' }},
                yaxis: {{ title: 'Сумма, млрд руб' }},
                height: 400,
                margin: {{ l: 60, r: 30, t: 30, b: 80 }}
            }};
            
            Plotly.newPlot('financialChart', [trace1, trace2], layout, {{responsive: true}});
        }}
        
        // График ROI
        function updateROIChart() {{
            const monthlyData = {{}};
            
            currentData.forEach(row => {{
                const month = row['Месяц_название'];
                if (!monthlyData[month]) {{
                    monthlyData[month] = {{costs: 0, income: 0}};
                }}
                monthlyData[month].costs += row['факт затраты'] || 0;
                monthlyData[month].income += row['доход факт'] || 0;
            }});
            
            const months = Object.keys(monthlyData).sort();
            const roiValues = months.map(m => 
                monthlyData[m].costs > 0 ? (monthlyData[m].income / monthlyData[m].costs * 100) : 0
            );
            
            const trace = {{
                x: months,
                y: roiValues,
                type: 'scatter',
                mode: 'lines+markers',
                fill: 'tozeroy',
                marker: {{ size: 10, color: '#e74c3c' }},
                line: {{ width: 3, color: '#e74c3c' }}
            }};
            
            const layout = {{
                xaxis: {{ title: 'Месяц' }},
                yaxis: {{ title: 'ROI, %' }},
                height: 400,
                margin: {{ l: 60, r: 30, t: 30, b: 80 }}
            }};
            
            Plotly.newPlot('roiChart', [trace], layout, {{responsive: true}});
        }}
        
        // Инициализация при загрузке
        window.addEventListener('DOMContentLoaded', () => {{
            initFilters();
            updateDashboard();
        }});
    </script>
</body>
</html>
"""

# Сохранение файла
output_file = '/workspace/interactive_dashboard.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n{'='*80}")
print("✅ ИНТЕРАКТИВНЫЙ ДАШБОРД СОЗДАН!")
print(f"{'='*80}")
print(f"\n📁 Файл: {output_file}")
print(f"📊 Размер: {len(html_content) / (1024*1024):.2f} MB")
print(f"\n🎯 ВОЗМОЖНОСТИ:")
print("   ✓ Выбор контракта из выпадающего списка")
print("   ✓ Фильтрация по сети, бренду, группе сбыта")
print("   ✓ Автоматическое обновление графиков")
print("   ✓ KPI метрики обновляются в реальном времени")
print("   ✓ Интерактивные графики Plotly")
print("   ✓ Работает локально без сервера")
print(f"\n🌐 ОТКРОЙТЕ ФАЙЛ В БРАУЗЕРЕ:")
print(f"   {output_file}")
print(f"\n{'='*80}")
