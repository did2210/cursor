"""
=================================================================================
ГЛАВНЫЙ СКРИПТ BI-ОТЧЕТА
=================================================================================
Комплексный анализ данных с созданием интерактивных дашбордов и отчетов

Использование:
    python main_bi_report.py

Для использования с данными с вашего компьютера:
    Измените переменную DATA_PATH на путь к вашему файлу
=================================================================================
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# НАСТРОЙКИ - ИЗМЕНИТЕ ПУТЬ К ВАШЕМУ ФАЙЛУ ЗДЕСЬ
# =============================================================================

# Для Windows используйте такой формат (ОБЯЗАТЕЛЬНО с буквой r перед кавычками!):
# DATA_PATH = r"\\FS\Users\Private\GFD\Public\Трейд-маркетинг\7.Общие документы\Гусев\итог\data.xlsx"

# Или можете использовать прямые слэши (работает в Windows):
# DATA_PATH = "//FS/Users/Private/GFD/Public/Трейд-маркетинг/7.Общие документы/Гусев/итог/data.xlsx"

# Для текущего рабочего каталога:
DATA_PATH = r'/workspace/data.xlsx'

OUTPUT_DIR = r'/workspace/reports'  # Папка для сохранения отчетов

# =============================================================================

# =============================================================================

def create_output_directory():
    """Создание директории для отчетов"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"✅ Создана директория: {OUTPUT_DIR}")

def load_and_prepare_data(file_path):
    """Загрузка и подготовка данных"""
    print("\n" + "="*80)
    print("📂 ЗАГРУЗКА ДАННЫХ")
    print("="*80)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    
    print(f"Чтение файла: {file_path}")
    df = pd.read_excel(file_path)
    
    # Подготовка данных
    df['Дата'] = pd.to_datetime(df['Дата'])
    df['Год'] = df['Дата'].dt.year
    df['Месяц'] = df['Дата'].dt.month
    df['Месяц_название'] = df['Дата'].dt.strftime('%Y-%m')
    df['Квартал'] = df['Дата'].dt.quarter
    df['Квартал_название'] = df['Дата'].dt.to_period('Q').astype(str)
    
    # Заполнение пропущенных значений
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    print(f"✅ Данных загружено: {len(df):,} строк x {len(df.columns)} столбцов")
    print(f"📅 Период: {df['Дата'].min().strftime('%Y-%m-%d')} → {df['Дата'].max().strftime('%Y-%m-%d')}")
    print(f"🏢 Уникальных контрактов: {df['Контракт'].nunique()}")
    print(f"🏪 Уникальных сетей: {df['Сеть'].nunique()}")
    print(f"🎯 Уникальных брендов: {df['Brand_format'].nunique()}")
    
    return df

def calculate_main_kpi(df):
    """Расчет основных KPI"""
    print("\n" + "="*80)
    print("📊 РАСЧЕТ KPI")
    print("="*80)
    
    kpi = {
        # Продажи
        'plan_sales_rub': df['Плановые продажи, руб'].sum(),
        'fact_sales_rub': df['Факт продажи, руб (от ЦМ)'].sum(),
        'plan_sales_units': df['Плановые продажи, шт'].sum(),
        'fact_sales_units': df['Факт продажи, шт.'].sum(),
        
        # Затраты
        'plan_costs': df['план затарты'].sum(),
        'fact_costs': df['факт затраты'].sum(),
        
        # Доход
        'plan_income': df['доход план'].sum(),
        'fact_income': df['доход факт'].sum(),
        
        # Себестоимость
        'plan_cost_price': df['сс план'].sum(),
        'fact_cost_price': df['сс факт'].sum(),
    }
    
    # Производные метрики
    kpi['fulfillment_rub_pct'] = (kpi['fact_sales_rub'] / kpi['plan_sales_rub'] * 100) if kpi['plan_sales_rub'] > 0 else 0
    kpi['fulfillment_units_pct'] = (kpi['fact_sales_units'] / kpi['plan_sales_units'] * 100) if kpi['plan_sales_units'] > 0 else 0
    kpi['costs_variance'] = kpi['fact_costs'] - kpi['plan_costs']
    kpi['income_variance'] = kpi['fact_income'] - kpi['plan_income']
    kpi['roi_plan'] = (kpi['plan_income'] / kpi['plan_costs'] * 100) if kpi['plan_costs'] > 0 else 0
    kpi['roi_fact'] = (kpi['fact_income'] / kpi['fact_costs'] * 100) if kpi['fact_costs'] > 0 else 0
    kpi['margin_plan'] = kpi['plan_sales_rub'] - kpi['plan_cost_price']
    kpi['margin_fact'] = kpi['fact_sales_rub'] - kpi['fact_cost_price']
    kpi['margin_pct_plan'] = (kpi['margin_plan'] / kpi['plan_sales_rub'] * 100) if kpi['plan_sales_rub'] > 0 else 0
    kpi['margin_pct_fact'] = (kpi['margin_fact'] / kpi['fact_sales_rub'] * 100) if kpi['fact_sales_rub'] > 0 else 0
    
    print("✅ KPI рассчитаны")
    return kpi

def create_visualizations(df, kpi):
    """Создание всех визуализаций"""
    print("\n" + "="*80)
    print("📈 СОЗДАНИЕ ВИЗУАЛИЗАЦИЙ")
    print("="*80)
    
    figures = {}
    
    # 1. План-Факт продаж по месяцам
    print("  1/10 График план-факт продаж...")
    monthly = df.groupby('Месяц_название').agg({
        'Плановые продажи, руб': 'sum',
        'Факт продажи, руб (от ЦМ)': 'sum',
        'Плановые продажи, шт': 'sum',
        'Факт продажи, шт.': 'sum'
    }).reset_index()
    
    fig1 = make_subplots(rows=2, cols=1,
                         subplot_titles=('Продажи в рублях', 'Продажи в штуках'),
                         vertical_spacing=0.12)
    
    fig1.add_trace(go.Bar(name='План (руб)', x=monthly['Месяц_название'],
                          y=monthly['Плановые продажи, руб'], marker_color='#3498db'), row=1, col=1)
    fig1.add_trace(go.Bar(name='Факт (руб)', x=monthly['Месяц_название'],
                          y=monthly['Факт продажи, руб (от ЦМ)'], marker_color='#2ecc71'), row=1, col=1)
    
    fig1.add_trace(go.Bar(name='План (шт)', x=monthly['Месяц_название'],
                          y=monthly['Плановые продажи, шт'], marker_color='#e67e22', showlegend=False), row=2, col=1)
    fig1.add_trace(go.Bar(name='Факт (шт)', x=monthly['Месяц_название'],
                          y=monthly['Факт продажи, шт.'], marker_color='#e74c3c', showlegend=False), row=2, col=1)
    
    fig1.update_layout(height=800, title_text="<b>Динамика продаж: План vs Факт</b>",
                      barmode='group', template='plotly_white')
    fig1.update_xaxes(tickangle=45)
    figures['sales_dynamics'] = fig1
    
    # 2. Процент выполнения плана
    print("  2/10 График выполнения плана...")
    monthly['Выполнение_руб_%'] = (monthly['Факт продажи, руб (от ЦМ)'] / 
                                    monthly['Плановые продажи, руб'] * 100).fillna(0)
    monthly['Выполнение_шт_%'] = (monthly['Факт продажи, шт.'] / 
                                   monthly['Плановые продажи, шт'] * 100).fillna(0)
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=monthly['Месяц_название'], y=monthly['Выполнение_руб_%'],
                             mode='lines+markers', name='Выполнение (руб)',
                             line=dict(width=3, color='#3498db'), marker=dict(size=10)))
    fig2.add_trace(go.Scatter(x=monthly['Месяц_название'], y=monthly['Выполнение_шт_%'],
                             mode='lines+markers', name='Выполнение (шт)',
                             line=dict(width=3, color='#2ecc71'), marker=dict(size=10)))
    fig2.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Целевой план (100%)")
    fig2.update_layout(title='<b>Процент выполнения плана</b>', height=500, template='plotly_white')
    fig2.update_xaxes(tickangle=45)
    figures['fulfillment'] = fig2
    
    # 3. Анализ затрат
    print("  3/10 График затрат...")
    cost_cats = {
        'Листинг': ['Плановые затраты «Листинг/безусловные выплаты», руб',
                   'Фактические затраты «Листинг/безусловные выплаты», руб'],
        'Скидка в цене': ['Плановые затраты «Скидка в цене», руб',
                         'Фактические затраты «Скидка в цене», руб'],
        'Ретро': ['Плановые затраты «Ретро», руб',
                 'Фактические затраты «Ретро», руб'],
        'Маркетинг': ['Плановые затраты «Маркетинг», руб',
                     'Фактические затраты «Маркетинг», руб'],
        'Промо-скидка': ['Плановые затраты «Промо-скидка», руб',
                        'Фактические затраты «Промо-скидка», руб']
    }
    
    costs_data = []
    for cat, cols in cost_cats.items():
        costs_data.append({
            'Категория': cat,
            'План': df[cols[0]].sum(),
            'Факт': df[cols[1]].sum()
        })
    
    costs_df = pd.DataFrame(costs_data)
    
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name='План', x=costs_df['Категория'], y=costs_df['План'],
                          marker_color='#95a5a6'))
    fig3.add_trace(go.Bar(name='Факт', x=costs_df['Категория'], y=costs_df['Факт'],
                          marker_color='#e74c3c'))
    fig3.update_layout(title='<b>Затраты по категориям</b>', barmode='group',
                      height=500, template='plotly_white')
    figures['costs'] = fig3
    
    # 4. Финансовые показатели
    print("  4/10 График финансовых показателей...")
    monthly_fin = df.groupby('Месяц_название').agg({
        'доход план': 'sum',
        'доход факт': 'sum',
        'план затарты': 'sum',
        'факт затраты': 'sum'
    }).reset_index()
    
    monthly_fin['ROI_план_%'] = (monthly_fin['доход план'] / monthly_fin['план затарты'] * 100).fillna(0)
    monthly_fin['ROI_факт_%'] = (monthly_fin['доход факт'] / monthly_fin['факт затраты'] * 100).fillna(0)
    
    fig4 = make_subplots(rows=2, cols=1,
                        subplot_titles=('Доход: План vs Факт', 'ROI по месяцам'),
                        vertical_spacing=0.12)
    
    fig4.add_trace(go.Bar(name='Доход План', x=monthly_fin['Месяц_название'],
                          y=monthly_fin['доход план'], marker_color='#3498db'), row=1, col=1)
    fig4.add_trace(go.Bar(name='Доход Факт', x=monthly_fin['Месяц_название'],
                          y=monthly_fin['доход факт'], marker_color='#2ecc71'), row=1, col=1)
    
    fig4.add_trace(go.Scatter(name='ROI План', x=monthly_fin['Месяц_название'],
                             y=monthly_fin['ROI_план_%'], mode='lines+markers',
                             line=dict(color='#e67e22', width=3), showlegend=False), row=2, col=1)
    fig4.add_trace(go.Scatter(name='ROI Факт', x=monthly_fin['Месяц_название'],
                             y=monthly_fin['ROI_факт_%'], mode='lines+markers',
                             line=dict(color='#e74c3c', width=3), showlegend=False), row=2, col=1)
    
    fig4.update_layout(height=800, title_text="<b>Финансовые показатели</b>",
                      barmode='group', template='plotly_white')
    fig4.update_xaxes(tickangle=45)
    figures['financial'] = fig4
    
    # 5. Анализ по группам сбыта
    print("  5/10 График по группам сбыта...")
    group_sales = df.groupby('группа сбыта').agg({
        'Факт продажи, руб (от ЦМ)': 'sum',
        'Плановые продажи, руб': 'sum'
    }).reset_index()
    
    fig5 = make_subplots(rows=1, cols=2, specs=[[{'type':'bar'}, {'type':'pie'}]],
                        subplot_titles=('Продажи по группам', 'Доля в продажах'))
    
    fig5.add_trace(go.Bar(name='План', x=group_sales['группа сбыта'],
                          y=group_sales['Плановые продажи, руб'], marker_color='#3498db'), row=1, col=1)
    fig5.add_trace(go.Bar(name='Факт', x=group_sales['группа сбыта'],
                          y=group_sales['Факт продажи, руб (от ЦМ)'], marker_color='#2ecc71'), row=1, col=1)
    
    fig5.add_trace(go.Pie(labels=group_sales['группа сбыта'],
                          values=group_sales['Факт продажи, руб (от ЦМ)'],
                          marker=dict(colors=['#3498db', '#2ecc71'])), row=1, col=2)
    
    fig5.update_layout(height=500, title_text="<b>Анализ по группам сбыта</b>",
                      template='plotly_white')
    figures['groups'] = fig5
    
    # 6. ТОП-10 сетей
    print("  6/10 График ТОП-10 сетей...")
    top_networks = df.groupby('Сеть')['Факт продажи, руб (от ЦМ)'].sum().sort_values(ascending=False).head(10)
    
    fig6 = go.Figure()
    fig6.add_trace(go.Bar(y=top_networks.index, x=top_networks.values, orientation='h',
                          marker=dict(color=top_networks.values, colorscale='Viridis', showscale=True)))
    fig6.update_layout(title='<b>ТОП-10 сетей по продажам</b>', height=500, template='plotly_white')
    figures['top_networks'] = fig6
    
    # 7. ТОП-15 брендов
    print("  7/10 График ТОП-15 брендов...")
    top_brands = df.groupby('Brand_format').agg({
        'Факт продажи, руб (от ЦМ)': 'sum',
        'Плановые продажи, руб': 'sum'
    }).reset_index()
    top_brands['Выполнение_%'] = (top_brands['Факт продажи, руб (от ЦМ)'] / 
                                   top_brands['Плановые продажи, руб'] * 100).fillna(0)
    top_brands = top_brands.sort_values('Факт продажи, руб (от ЦМ)', ascending=False).head(15)
    
    fig7 = go.Figure()
    fig7.add_trace(go.Bar(y=top_brands['Brand_format'], x=top_brands['Факт продажи, руб (от ЦМ)'],
                          orientation='h',
                          marker=dict(color=top_brands['Выполнение_%'],
                                     colorscale='RdYlGn', showscale=True,
                                     colorbar=dict(title="Выполнение, %")),
                          text=top_brands['Выполнение_%'].apply(lambda x: f'{x:.1f}%'),
                          textposition='outside'))
    fig7.update_layout(title='<b>ТОП-15 брендов по продажам</b>', height=600, template='plotly_white')
    figures['top_brands'] = fig7
    
    # 8. Тепловая карта
    print("  8/10 Тепловая карта...")
    heatmap = df.groupby(['Месяц_название', 'группа сбыта']).agg({
        'Факт продажи, руб (от ЦМ)': 'sum',
        'Плановые продажи, руб': 'sum'
    }).reset_index()
    heatmap['Выполнение_%'] = (heatmap['Факт продажи, руб (от ЦМ)'] / 
                                heatmap['Плановые продажи, руб'] * 100).fillna(0)
    heatmap_pivot = heatmap.pivot(index='группа сбыта', columns='Месяц_название',
                                   values='Выполнение_%')
    
    fig8 = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        colorscale='RdYlGn',
        zmid=100,
        text=np.round(heatmap_pivot.values, 1),
        texttemplate='%{text}%',
        textfont={"size": 14},
        colorbar=dict(title="Выполнение, %")
    ))
    fig8.update_layout(title='<b>Тепловая карта выполнения плана</b>', height=400, template='plotly_white')
    fig8.update_xaxes(tickangle=45)
    figures['heatmap'] = fig8
    
    # 9. Квартальная динамика
    print("  9/10 Квартальная динамика...")
    quarterly = df.groupby('Квартал_название').agg({
        'Факт продажи, руб (от ЦМ)': 'sum',
        'Плановые продажи, руб': 'sum',
        'факт затраты': 'sum',
        'доход факт': 'sum'
    }).reset_index()
    quarterly['ROI_%'] = (quarterly['доход факт'] / quarterly['факт затраты'] * 100).fillna(0)
    
    fig9 = make_subplots(rows=2, cols=1,
                        subplot_titles=('Квартальные продажи', 'Квартальный ROI'),
                        vertical_spacing=0.12)
    
    fig9.add_trace(go.Bar(name='План', x=quarterly['Квартал_название'],
                          y=quarterly['Плановые продажи, руб'], marker_color='#3498db'), row=1, col=1)
    fig9.add_trace(go.Bar(name='Факт', x=quarterly['Квартал_название'],
                          y=quarterly['Факт продажи, руб (от ЦМ)'], marker_color='#2ecc71'), row=1, col=1)
    
    fig9.add_trace(go.Scatter(x=quarterly['Квартал_название'], y=quarterly['ROI_%'],
                             mode='lines+markers', line=dict(color='#e74c3c', width=3),
                             marker=dict(size=12), showlegend=False), row=2, col=1)
    
    fig9.update_layout(height=700, title_text="<b>Квартальная динамика</b>",
                      barmode='group', template='plotly_white')
    figures['quarterly'] = fig9
    
    # 10. Воронка продаж
    print("  10/10 Воронка продаж...")
    funnel_data = pd.DataFrame({
        'Этап': ['План продаж', 'Факт продаж', 'Затраты', 'Доход'],
        'Значение': [kpi['plan_sales_rub'], kpi['fact_sales_rub'],
                    kpi['fact_costs'], kpi['fact_income']]
    })
    
    fig10 = px.funnel(funnel_data, x='Значение', y='Этап', color='Этап',
                     title='<b>Финансовая воронка</b>')
    fig10.update_layout(height=600, template='plotly_white')
    figures['funnel'] = fig10
    
    print("✅ Все визуализации созданы")
    return figures

def create_html_report(df, kpi, figures):
    """Создание HTML отчета"""
    print("\n" + "="*80)
    print("📄 СОЗДАНИЕ HTML ОТЧЕТА")
    print("="*80)
    
    def kpi_card(title, value, unit='', color='#3498db'):
        return f"""
        <div style="background: linear-gradient(135deg, {color} 0%, {color}dd 100%);
                    padding: 20px; border-radius: 10px; margin: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1); color: white;">
            <div style="font-size: 14px; opacity: 0.9;">{title}</div>
            <div style="font-size: 28px; font-weight: bold; margin-top: 10px;">
                {value:,.0f}{unit}
            </div>
        </div>
        """
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>BI Dashboard - Комплексный анализ</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            font-size: 42px;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #7f8c8d;
            font-size: 18px;
            margin-bottom: 40px;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 40px 0;
        }}
        .section {{
            margin: 50px 0;
        }}
        .section-title {{
            color: #2c3e50;
            font-size: 28px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #3498db;
        }}
        .chart-container {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 10px;
            margin: 30px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .summary-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin: 30px 0;
        }}
        .summary-box h3 {{
            margin-bottom: 20px;
            font-size: 24px;
        }}
        .summary-box ul {{
            list-style: none;
            padding: 0;
        }}
        .summary-box li {{
            padding: 10px 0;
            font-size: 16px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }}
        .footer {{
            text-align: center;
            margin-top: 60px;
            padding-top: 30px;
            border-top: 2px solid #ddd;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 BI Dashboard - Комплексный анализ продаж</h1>
        <div class="subtitle">
            Период: {df['Дата'].min().strftime('%d.%m.%Y')} - {df['Дата'].max().strftime('%d.%m.%Y')} |
            Обработано: {len(df):,} записей
        </div>
        
        <!-- KPI Карточки -->
        <div class="section">
            <div class="section-title">🎯 Ключевые показатели эффективности (KPI)</div>
            <div class="kpi-grid">
                {kpi_card("Продажи План", kpi['plan_sales_rub'], ' ₽', '#3498db')}
                {kpi_card("Продажи Факт", kpi['fact_sales_rub'], ' ₽', '#2ecc71')}
                {kpi_card("Выполнение плана", kpi['fulfillment_rub_pct'], '%', '#9b59b6')}
                {kpi_card("Доход Факт", kpi['fact_income'], ' ₽', '#1abc9c')}
                {kpi_card("ROI Факт", kpi['roi_fact'], '%', '#e67e22')}
                {kpi_card("Маржинальность", kpi['margin_pct_fact'], '%', '#e74c3c')}
            </div>
        </div>
        
        <!-- Резюме -->
        <div class="summary-box">
            <h3>📈 Основные выводы</h3>
            <ul>
                <li>💰 Общий объем продаж: {kpi['fact_sales_rub']:,.0f} руб ({kpi['fulfillment_rub_pct']:.1f}% от плана)</li>
                <li>📦 Продано единиц: {kpi['fact_sales_units']:,.0f} шт ({kpi['fulfillment_units_pct']:.1f}% от плана)</li>
                <li>💵 Фактические затраты: {kpi['fact_costs']:,.0f} руб</li>
                <li>✅ Фактический доход: {kpi['fact_income']:,.0f} руб</li>
                <li>📊 ROI (рентабельность инвестиций): {kpi['roi_fact']:.1f}%</li>
                <li>📈 Маржа: {kpi['margin_fact']:,.0f} руб ({kpi['margin_pct_fact']:.1f}%)</li>
                <li>🏪 Работаем с {df['Сеть'].nunique()} сетями</li>
                <li>🎯 Анализируем {df['Brand_format'].nunique()} брендов</li>
            </ul>
        </div>
        
        <!-- Графики -->
        <div class="section">
            <div class="section-title">📊 Визуализация данных</div>
            
            <div class="chart-container">
                {figures['sales_dynamics'].to_html(full_html=False, include_plotlyjs='cdn')}
            </div>
            
            <div class="chart-container">
                {figures['fulfillment'].to_html(full_html=False, include_plotlyjs=False)}
            </div>
            
            <div class="chart-container">
                {figures['heatmap'].to_html(full_html=False, include_plotlyjs=False)}
            </div>
            
            <div class="chart-container">
                {figures['costs'].to_html(full_html=False, include_plotlyjs=False)}
            </div>
            
            <div class="chart-container">
                {figures['financial'].to_html(full_html=False, include_plotlyjs=False)}
            </div>
            
            <div class="chart-container">
                {figures['groups'].to_html(full_html=False, include_plotlyjs=False)}
            </div>
            
            <div class="chart-container">
                {figures['top_brands'].to_html(full_html=False, include_plotlyjs=False)}
            </div>
            
            <div class="chart-container">
                {figures['top_networks'].to_html(full_html=False, include_plotlyjs=False)}
            </div>
            
            <div class="chart-container">
                {figures['quarterly'].to_html(full_html=False, include_plotlyjs=False)}
            </div>
            
            <div class="chart-container">
                {figures['funnel'].to_html(full_html=False, include_plotlyjs=False)}
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p style="font-size: 18px; margin-bottom: 10px;">
                <strong>Отчет сгенерирован: {datetime.now().strftime('%d.%m.%Y в %H:%M:%S')}</strong>
            </p>
            <p>Источник: {os.path.basename(DATA_PATH)}</p>
            <p>Всего графиков: {len(figures)} | KPI метрик: 20+</p>
        </div>
    </div>
</body>
</html>
    """
    
    output_file = os.path.join(OUTPUT_DIR, 'complete_bi_dashboard.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ HTML отчет сохранен: {output_file}")
    return output_file

def create_excel_export(df):
    """Создание Excel отчета"""
    print("\n" + "="*80)
    print("📊 СОЗДАНИЕ EXCEL ОТЧЕТА")
    print("="*80)
    
    output_file = os.path.join(OUTPUT_DIR, 'analytics_export.xlsx')
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # 1. Общая сводка
        summary = pd.DataFrame({
            'Метрика': ['Период', 'Записей', 'План продаж (руб)', 'Факт продаж (руб)',
                       'Выполнение (%)', 'Затраты факт', 'Доход факт', 'ROI (%)'],
            'Значение': [
                f"{df['Дата'].min().strftime('%Y-%m-%d')} - {df['Дата'].max().strftime('%Y-%m-%d')}",
                len(df),
                df['Плановые продажи, руб'].sum(),
                df['Факт продажи, руб (от ЦМ)'].sum(),
                df['Факт продажи, руб (от ЦМ)'].sum() / df['Плановые продажи, руб'].sum() * 100,
                df['факт затраты'].sum(),
                df['доход факт'].sum(),
                df['доход факт'].sum() / df['факт затраты'].sum() * 100
            ]
        })
        summary.to_excel(writer, sheet_name='Сводка', index=False)
        
        # 2. По месяцам
        monthly = df.groupby('Месяц_название').agg({
            'Плановые продажи, руб': 'sum',
            'Факт продажи, руб (от ЦМ)': 'sum',
            'план затарты': 'sum',
            'факт затраты': 'sum',
            'доход факт': 'sum'
        }).reset_index()
        monthly['Выполнение_%'] = (monthly['Факт продажи, руб (от ЦМ)'] / 
                                    monthly['Плановые продажи, руб'] * 100).round(2)
        monthly.to_excel(writer, sheet_name='По месяцам', index=False)
        
        # 3. По брендам
        brands = df.groupby('Brand_format').agg({
            'Факт продажи, руб (от ЦМ)': 'sum',
            'Плановые продажи, руб': 'sum',
            'факт затраты': 'sum',
            'доход факт': 'sum'
        }).sort_values('Факт продажи, руб (от ЦМ)', ascending=False)
        brands.to_excel(writer, sheet_name='По брендам')
        
        # 4. По сетям
        networks = df.groupby('Сеть').agg({
            'Факт продажи, руб (от ЦМ)': 'sum',
            'Плановые продажи, руб': 'sum'
        }).sort_values('Факт продажи, руб (от ЦМ)', ascending=False).head(50)
        networks.to_excel(writer, sheet_name='ТОП-50 сетей')
        
        # 5. По группам сбыта
        groups = df.groupby('группа сбыта').agg({
            'Факт продажи, руб (от ЦМ)': 'sum',
            'Плановые продажи, руб': 'sum',
            'факт затраты': 'sum',
            'доход факт': 'sum'
        })
        groups.to_excel(writer, sheet_name='По группам сбыта')
    
    print(f"✅ Excel отчет сохранен: {output_file}")
    return output_file

def main():
    """Главная функция"""
    print("\n")
    print("="*80)
    print("                     BI DASHBOARD - АНАЛИЗ ДАННЫХ                    ")
    print("="*80)
    print(f"Начало работы: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    
    try:
        # Создание директории для отчетов
        create_output_directory()
        
        # Загрузка данных
        df = load_and_prepare_data(DATA_PATH)
        
        # Расчет KPI
        kpi = calculate_main_kpi(df)
        
        # Создание визуализаций
        figures = create_visualizations(df, kpi)
        
        # Создание отчетов
        html_file = create_html_report(df, kpi, figures)
        excel_file = create_excel_export(df)
        
        # Итоговая информация
        print("\n" + "="*80)
        print("✅ ВСЕ ОТЧЕТЫ УСПЕШНО СОЗДАНЫ!")
        print("="*80)
        print(f"\n📁 Созданные файлы:")
        print(f"   1. {html_file}")
        print(f"      → Интерактивный HTML дашборд с 10 графиками")
        print(f"   2. {excel_file}")
        print(f"      → Excel файл с 5 вкладками детального анализа")
        
        print(f"\n📊 Статистика:")
        print(f"   • Обработано записей: {len(df):,}")
        print(f"   • План продаж: {kpi['plan_sales_rub']:,.0f} руб")
        print(f"   • Факт продаж: {kpi['fact_sales_rub']:,.0f} руб")
        print(f"   • Выполнение плана: {kpi['fulfillment_rub_pct']:.1f}%")
        print(f"   • ROI: {kpi['roi_fact']:.1f}%")
        
        print(f"\n🌐 Откройте {html_file} в браузере для просмотра дашборда")
        print(f"📊 Откройте {excel_file} в Excel для детального анализа")
        
        print(f"\n⏱️  Время завершения: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
