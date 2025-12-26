#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор статического HTML отчета с интерактивными графиками
Альтернатива Dash дашборду - создает один HTML файл
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import os

def load_data(file_path=None):
    """Загружает и подготавливает данные из Excel"""
    if file_path is None:
        file_path = os.environ.get('DATA_FILE_PATH', 'data.xlsx')
    
    print(f"📂 Загрузка данных из: {file_path}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    
    df = pd.read_excel(file_path)
    
    # Заполняем пропуски
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].fillna(0)
    
    # Добавляем расчетные поля
    df['Выполнение плана продаж, %'] = np.where(
        df['Плановые продажи, руб'] != 0,
        (df['Факт продажи, руб (от ЦМ)'] / df['Плановые продажи, руб'] * 100),
        0
    )
    
    return df

def generate_html_report(df, output_file='bi_report.html'):
    """Генерирует HTML отчет с графиками"""
    
    print("📊 Создание графиков...")
    
    # 1. План/Факт продаж по месяцам
    monthly_data = df.groupby('Дата').agg({
        'Плановые продажи, руб': 'sum',
        'Факт продажи, руб (от ЦМ)': 'sum',
        'доход план': 'sum',
        'доход факт': 'sum'
    }).reset_index()
    
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=monthly_data['Дата'],
        y=monthly_data['Плановые продажи, руб'],
        name='План продажи',
        marker_color='lightblue',
        opacity=0.7
    ))
    fig1.add_trace(go.Bar(
        x=monthly_data['Дата'],
        y=monthly_data['Факт продажи, руб (от ЦМ)'],
        name='Факт продажи',
        marker_color='darkblue'
    ))
    fig1.update_layout(
        title='План/Факт продаж по месяцам (руб)',
        xaxis_title='Месяц',
        yaxis_title='Продажи, руб',
        barmode='group',
        height=500,
        template='plotly_white'
    )
    
    # 2. Динамика выполнения плана
    monthly_data['Выполнение плана, %'] = (
        monthly_data['Факт продажи, руб (от ЦМ)'] / 
        monthly_data['Плановые продажи, руб'] * 100
    )
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=monthly_data['Дата'],
        y=monthly_data['Выполнение плана, %'],
        mode='lines+markers',
        name='Выполнение плана',
        line=dict(color='blue', width=3),
        marker=dict(size=10),
        fill='tonexty'
    ))
    fig2.add_hline(y=100, line_dash="dash", line_color="red", 
                  annotation_text="Цель 100%")
    fig2.update_layout(
        title='Динамика выполнения плана продаж',
        xaxis_title='Месяц',
        yaxis_title='Выполнение плана, %',
        height=500,
        template='plotly_white'
    )
    
    # 3. ТОП торговых сетей
    network_data = df.groupby('Сеть').agg({
        'Факт продажи, руб (от ЦМ)': 'sum'
    }).reset_index()
    network_data = network_data.sort_values('Факт продажи, руб (от ЦМ)', ascending=False).head(15)
    
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        y=network_data['Сеть'],
        x=network_data['Факт продажи, руб (от ЦМ)'],
        orientation='h',
        marker_color='steelblue',
        text=network_data['Факт продажи, руб (от ЦМ)'].apply(lambda x: f'{x/1e6:.1f}M'),
        textposition='auto'
    ))
    fig3.update_layout(
        title='ТОП-15 торговых сетей по продажам',
        xaxis_title='Продажи, руб',
        yaxis_title='',
        height=600,
        template='plotly_white'
    )
    
    # 4. ТОП продуктов с выполнением плана
    product_data = df.groupby('Brand_format').agg({
        'Плановые продажи, руб': 'sum',
        'Факт продажи, руб (от ЦМ)': 'sum'
    }).reset_index()
    product_data['Выполнение плана, %'] = (
        product_data['Факт продажи, руб (от ЦМ)'] / 
        product_data['Плановые продажи, руб'] * 100
    )
    product_data = product_data.sort_values('Факт продажи, руб (от ЦМ)', ascending=True).tail(15)
    
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        y=product_data['Brand_format'],
        x=product_data['Факт продажи, руб (от ЦМ)'],
        orientation='h',
        marker=dict(
            color=product_data['Выполнение плана, %'],
            colorscale='RdYlGn',
            cmin=0,
            cmax=150,
            colorbar=dict(title="Выполнение<br>плана, %")
        ),
        text=product_data['Выполнение плана, %'].apply(lambda x: f'{x:.0f}%'),
        textposition='auto'
    ))
    fig4.update_layout(
        title='ТОП-15 продуктов по продажам (цвет = выполнение плана)',
        xaxis_title='Продажи, руб',
        yaxis_title='',
        height=600,
        template='plotly_white'
    )
    
    # 5. Затраты по типам
    costs_data = {
        'Тип затрат': [
            'Листинг',
            'Скидка в цене',
            'Ретро',
            'Маркетинг',
            'Промо-скидка'
        ],
        'План': [
            df['Плановые затраты «Листинг/безусловные выплаты», руб'].sum(),
            df['Плановые затраты «Скидка в цене», руб'].sum(),
            df['Плановые затраты «Ретро», руб'].sum(),
            df['Плановые затраты «Маркетинг», руб'].sum(),
            df['Плановые затраты «Промо-скидка», руб'].sum()
        ],
        'Факт': [
            df['Фактические затраты «Листинг/безусловные выплаты», руб'].sum(),
            df['Фактические затраты «Скидка в цене», руб'].sum(),
            df['Фактические затраты «Ретро», руб'].sum(),
            df['Фактические затраты «Маркетинг», руб'].sum(),
            df['Фактические затраты «Промо-скидка», руб'].sum()
        ]
    }
    costs_df = pd.DataFrame(costs_data)
    
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(
        x=costs_df['Тип затрат'],
        y=costs_df['План'],
        name='План',
        marker_color='lightcoral'
    ))
    fig5.add_trace(go.Bar(
        x=costs_df['Тип затрат'],
        y=costs_df['Факт'],
        name='Факт',
        marker_color='darkred'
    ))
    fig5.update_layout(
        title='План/Факт затрат по типам',
        xaxis_title='Тип затрат',
        yaxis_title='Сумма, руб',
        barmode='group',
        height=500,
        template='plotly_white'
    )
    
    # 6. Доходы vs Затраты
    monthly_fin = df.groupby('Дата').agg({
        'доход факт': 'sum',
        'факт затраты': 'sum',
        'Факт продажи, руб (от ЦМ)': 'sum'
    }).reset_index()
    monthly_fin['Рентабельность, %'] = (
        monthly_fin['доход факт'] / monthly_fin['Факт продажи, руб (от ЦМ)'] * 100
    )
    
    fig6 = make_subplots(specs=[[{"secondary_y": True}]])
    fig6.add_trace(
        go.Bar(x=monthly_fin['Дата'], y=monthly_fin['доход факт'],
               name='Доход', marker_color='lightgreen'),
        secondary_y=False
    )
    fig6.add_trace(
        go.Bar(x=monthly_fin['Дата'], y=monthly_fin['факт затраты'],
               name='Затраты', marker_color='lightcoral'),
        secondary_y=False
    )
    fig6.add_trace(
        go.Scatter(x=monthly_fin['Дата'], y=monthly_fin['Рентабельность, %'],
                   name='Рентабельность, %', line=dict(color='blue', width=3),
                   mode='lines+markers'),
        secondary_y=True
    )
    fig6.update_layout(
        title='Доходы, затраты и рентабельность',
        height=500,
        template='plotly_white'
    )
    fig6.update_xaxes(title_text="Месяц")
    fig6.update_yaxes(title_text="Сумма, руб", secondary_y=False)
    fig6.update_yaxes(title_text="Рентабельность, %", secondary_y=True)
    
    # 7. Распределение по группам сбыта
    group_data = df.groupby('группа сбыта2').agg({
        'Факт продажи, руб (от ЦМ)': 'sum'
    }).reset_index()
    
    fig7 = go.Figure(data=[
        go.Pie(
            labels=group_data['группа сбыта2'],
            values=group_data['Факт продажи, руб (от ЦМ)'],
            hole=0.4,
            marker_colors=px.colors.qualitative.Set3
        )
    ])
    fig7.update_layout(
        title='Распределение продаж по группам сбыта',
        height=500,
        template='plotly_white'
    )
    
    # Расчет KPI
    total_plan_sales = df['Плановые продажи, руб'].sum()
    total_fact_sales = df['Факт продажи, руб (от ЦМ)'].sum()
    plan_execution = (total_fact_sales / total_plan_sales * 100) if total_plan_sales > 0 else 0
    
    total_plan_income = df['доход план'].sum()
    total_fact_income = df['доход факт'].sum()
    income_execution = (total_fact_income / total_plan_income * 100) if total_plan_income > 0 else 0
    
    total_plan_costs = df['план затарты'].sum()
    total_fact_costs = df['факт затраты'].sum()
    
    total_plan_units = df['Плановые продажи, шт'].sum()
    total_fact_units = df['Факт продажи, шт.'].sum()
    units_execution = (total_fact_units / total_plan_units * 100) if total_plan_units > 0 else 0
    
    # Генерация HTML
    print("📝 Генерация HTML...")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BI Отчет - Анализ продаж</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                text-align: center;
                color: #2c3e50;
                margin-bottom: 30px;
            }}
            .kpi-container {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            .kpi-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                border-radius: 10px;
                color: white;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .kpi-card h3 {{
                margin: 0 0 10px 0;
                font-size: 16px;
                opacity: 0.9;
            }}
            .kpi-card .value {{
                font-size: 32px;
                font-weight: bold;
                margin: 10px 0;
            }}
            .kpi-card .subtext {{
                font-size: 14px;
                opacity: 0.8;
            }}
            .kpi-card .execution {{
                font-size: 20px;
                font-weight: bold;
                margin-top: 10px;
            }}
            .kpi-card.green {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }}
            .kpi-card.blue {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
            .kpi-card.orange {{ background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }}
            .kpi-card.red {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
            
            .chart-container {{
                margin: 30px 0;
                padding: 20px;
                background: white;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                color: #999;
            }}
            .grid-2 {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }}
            @media (max-width: 768px) {{
                .grid-2 {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 BI Отчет - Анализ продаж и затрат</h1>
            
            <div class="kpi-container">
                <div class="kpi-card blue">
                    <h3>💰 Продажи (руб)</h3>
                    <div class="value">{total_fact_sales:,.0f}</div>
                    <div class="subtext">План: {total_plan_sales:,.0f}</div>
                    <div class="execution">{plan_execution:.1f}% выполнения</div>
                </div>
                
                <div class="kpi-card orange">
                    <h3>📦 Продажи (шт)</h3>
                    <div class="value">{total_fact_units:,.0f}</div>
                    <div class="subtext">План: {total_plan_units:,.0f}</div>
                    <div class="execution">{units_execution:.1f}% выполнения</div>
                </div>
                
                <div class="kpi-card green">
                    <h3>💵 Доход</h3>
                    <div class="value">{total_fact_income:,.0f}</div>
                    <div class="subtext">План: {total_plan_income:,.0f}</div>
                    <div class="execution">{income_execution:.1f}% выполнения</div>
                </div>
                
                <div class="kpi-card red">
                    <h3>💸 Затраты</h3>
                    <div class="value">{total_fact_costs:,.0f}</div>
                    <div class="subtext">План: {total_plan_costs:,.0f}</div>
                    <div class="execution">{(total_fact_costs/total_plan_costs*100):.1f}% от плана</div>
                </div>
            </div>
            
            <div class="chart-container">
                <div id="chart1"></div>
            </div>
            
            <div class="chart-container">
                <div id="chart2"></div>
            </div>
            
            <div class="grid-2">
                <div class="chart-container">
                    <div id="chart3"></div>
                </div>
                <div class="chart-container">
                    <div id="chart4"></div>
                </div>
            </div>
            
            <div class="grid-2">
                <div class="chart-container">
                    <div id="chart5"></div>
                </div>
                <div class="chart-container">
                    <div id="chart6"></div>
                </div>
            </div>
            
            <div class="chart-container">
                <div id="chart7"></div>
            </div>
            
            <div class="footer">
                <p>Отчет сгенерирован: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Данные: data.xlsx | Период: {df['Дата'].min().strftime('%Y-%m')} - {df['Дата'].max().strftime('%Y-%m')}</p>
            </div>
        </div>
        
        <script>
            Plotly.newPlot('chart1', {fig1.to_json()});
            Plotly.newPlot('chart2', {fig2.to_json()});
            Plotly.newPlot('chart3', {fig3.to_json()});
            Plotly.newPlot('chart4', {fig4.to_json()});
            Plotly.newPlot('chart5', {fig5.to_json()});
            Plotly.newPlot('chart6', {fig6.to_json()});
            Plotly.newPlot('chart7', {fig7.to_json()});
        </script>
    </body>
    </html>
    """
    
    # Вставляем JSON графиков
    html_content = html_content.replace('{fig1.to_json()}', fig1.to_json())
    html_content = html_content.replace('{fig2.to_json()}', fig2.to_json())
    html_content = html_content.replace('{fig3.to_json()}', fig3.to_json())
    html_content = html_content.replace('{fig4.to_json()}', fig4.to_json())
    html_content = html_content.replace('{fig5.to_json()}', fig5.to_json())
    html_content = html_content.replace('{fig6.to_json()}', fig6.to_json())
    html_content = html_content.replace('{fig7.to_json()}', fig7.to_json())
    
    # Сохранение
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML отчет сохранен: {output_file}")
    print(f"📂 Полный путь: {os.path.abspath(output_file)}")
    return output_file

def main():
    """Основная функция"""
    print("="*80)
    print("📊 ГЕНЕРАТОР HTML ОТЧЕТА")
    print("="*80)
    
    try:
        # Загрузка данных
        df = load_data()
        print(f"✅ Загружено записей: {len(df)}")
        
        # Генерация отчета
        output_file = generate_html_report(df)
        
        print("\n" + "="*80)
        print("🎉 ГОТОВО!")
        print("="*80)
        print(f"\n📄 Откройте файл в браузере: {output_file}")
        print("\n💡 Просто дважды кликните на файл или перетащите в браузер")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
