"""
BI Dashboard - Анализ продаж и затрат
Создает интерактивный HTML-отчет с метриками и графиками
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# ЗАГРУЗКА И ПОДГОТОВКА ДАННЫХ
# ============================================================================

print("Загрузка данных...")
df = pd.read_excel('/workspace/data.xlsx')

# Очистка и подготовка данных
df['Дата'] = pd.to_datetime(df['Дата'])
df['Год'] = df['Дата'].dt.year
df['Месяц'] = df['Дата'].dt.month
df['Месяц_название'] = df['Дата'].dt.strftime('%Y-%m')
df['Квартал'] = df['Дата'].dt.quarter

# Заполнение пропущенных значений нулями для расчетов
numeric_cols = df.select_dtypes(include=[np.number]).columns
df[numeric_cols] = df[numeric_cols].fillna(0)

print(f"Данных загружено: {len(df):,} строк")
print(f"Период: {df['Дата'].min().strftime('%Y-%m-%d')} - {df['Дата'].max().strftime('%Y-%m-%d')}")

# ============================================================================
# РАСЧЕТ KPI И МЕТРИК
# ============================================================================

def calculate_kpi(df):
    """Расчет ключевых показателей эффективности"""
    
    kpi = {}
    
    # Продажи
    kpi['plan_sales_units'] = df['Плановые продажи, шт'].sum()
    kpi['fact_sales_units'] = df['Факт продажи, шт.'].sum()
    kpi['plan_sales_rub'] = df['Плановые продажи, руб'].sum()
    kpi['fact_sales_rub'] = df['Факт продажи, руб (от ЦМ)'].sum()
    
    # Процент выполнения плана
    kpi['fulfillment_units'] = (kpi['fact_sales_units'] / kpi['plan_sales_units'] * 100) if kpi['plan_sales_units'] > 0 else 0
    kpi['fulfillment_rub'] = (kpi['fact_sales_rub'] / kpi['plan_sales_rub'] * 100) if kpi['plan_sales_rub'] > 0 else 0
    
    # Затраты
    kpi['plan_costs'] = df['план затарты'].sum()
    kpi['fact_costs'] = df['факт затраты'].sum()
    kpi['costs_variance'] = kpi['fact_costs'] - kpi['plan_costs']
    kpi['costs_variance_pct'] = (kpi['costs_variance'] / kpi['plan_costs'] * 100) if kpi['plan_costs'] > 0 else 0
    
    # Доход
    kpi['plan_income'] = df['доход план'].sum()
    kpi['fact_income'] = df['доход факт'].sum()
    kpi['income_variance'] = kpi['fact_income'] - kpi['plan_income']
    kpi['income_variance_pct'] = (kpi['income_variance'] / kpi['plan_income'] * 100) if kpi['plan_income'] > 0 else 0
    
    # ROI
    kpi['roi_plan'] = (kpi['plan_income'] / kpi['plan_costs'] * 100) if kpi['plan_costs'] > 0 else 0
    kpi['roi_fact'] = (kpi['fact_income'] / kpi['fact_costs'] * 100) if kpi['fact_costs'] > 0 else 0
    
    return kpi

kpi = calculate_kpi(df)

# ============================================================================
# СОЗДАНИЕ ДАШБОРДА
# ============================================================================

def create_kpi_card(title, value, unit='', color='blue'):
    """Создание карточки KPI"""
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

# ============================================================================
# ГРАФИКИ
# ============================================================================

print("Создание графиков...")

# 1. План-Факт продаж по месяцам
monthly_sales = df.groupby('Месяц_название').agg({
    'Плановые продажи, руб': 'sum',
    'Факт продажи, руб (от ЦМ)': 'sum',
    'Плановые продажи, шт': 'sum',
    'Факт продажи, шт.': 'sum'
}).reset_index()

fig1 = make_subplots(
    rows=2, cols=1,
    subplot_titles=('Продажи в рублях (План vs Факт)', 'Продажи в штуках (План vs Факт)'),
    vertical_spacing=0.12
)

fig1.add_trace(
    go.Bar(name='План (руб)', x=monthly_sales['Месяц_название'], 
           y=monthly_sales['Плановые продажи, руб'], marker_color='lightblue'),
    row=1, col=1
)
fig1.add_trace(
    go.Bar(name='Факт (руб)', x=monthly_sales['Месяц_название'], 
           y=monthly_sales['Факт продажи, руб (от ЦМ)'], marker_color='darkblue'),
    row=1, col=1
)

fig1.add_trace(
    go.Bar(name='План (шт)', x=monthly_sales['Месяц_название'], 
           y=monthly_sales['Плановые продажи, шт'], marker_color='lightgreen', showlegend=False),
    row=2, col=1
)
fig1.add_trace(
    go.Bar(name='Факт (шт)', x=monthly_sales['Месяц_название'], 
           y=monthly_sales['Факт продажи, шт.'], marker_color='darkgreen', showlegend=False),
    row=2, col=1
)

fig1.update_layout(height=800, title_text="<b>Динамика продаж: План vs Факт</b>", 
                   barmode='group', template='plotly_white')
fig1.update_xaxes(tickangle=45)

# 2. Процент выполнения плана по месяцам
monthly_sales['Выполнение плана (руб), %'] = (monthly_sales['Факт продажи, руб (от ЦМ)'] / 
                                                monthly_sales['Плановые продажи, руб'] * 100)
monthly_sales['Выполнение плана (шт), %'] = (monthly_sales['Факт продажи, шт.'] / 
                                               monthly_sales['Плановые продажи, шт'] * 100)

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=monthly_sales['Месяц_название'],
    y=monthly_sales['Выполнение плана (руб), %'],
    mode='lines+markers',
    name='Выполнение плана (руб)',
    line=dict(width=3, color='#2E86DE'),
    marker=dict(size=10)
))
fig2.add_trace(go.Scatter(
    x=monthly_sales['Месяц_название'],
    y=monthly_sales['Выполнение плана (шт), %'],
    mode='lines+markers',
    name='Выполнение плана (шт)',
    line=dict(width=3, color='#10AC84'),
    marker=dict(size=10)
))
fig2.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Целевой план (100%)")
fig2.update_layout(
    title='<b>Процент выполнения плана по месяцам</b>',
    xaxis_title='Месяц',
    yaxis_title='Выполнение плана, %',
    height=500,
    template='plotly_white'
)
fig2.update_xaxes(tickangle=45)

# 3. Анализ затрат по категориям
cost_categories = {
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
for category, cols in cost_categories.items():
    costs_data.append({
        'Категория': category,
        'План': df[cols[0]].sum(),
        'Факт': df[cols[1]].sum()
    })

costs_df = pd.DataFrame(costs_data)
costs_df['Отклонение'] = costs_df['Факт'] - costs_df['План']
costs_df['Отклонение, %'] = (costs_df['Отклонение'] / costs_df['План'] * 100).fillna(0)

fig3 = go.Figure()
fig3.add_trace(go.Bar(
    name='План',
    x=costs_df['Категория'],
    y=costs_df['План'],
    marker_color='lightcoral'
))
fig3.add_trace(go.Bar(
    name='Факт',
    x=costs_df['Категория'],
    y=costs_df['Факт'],
    marker_color='darkred'
))
fig3.update_layout(
    title='<b>Затраты по категориям: План vs Факт</b>',
    xaxis_title='Категория затрат',
    yaxis_title='Сумма, руб',
    barmode='group',
    height=500,
    template='plotly_white'
)

# 4. Доход и ROI по месяцам
monthly_income = df.groupby('Месяц_название').agg({
    'доход план': 'sum',
    'доход факт': 'sum',
    'план затарты': 'sum',
    'факт затраты': 'sum'
}).reset_index()

monthly_income['ROI план, %'] = (monthly_income['доход план'] / monthly_income['план затарты'] * 100).fillna(0)
monthly_income['ROI факт, %'] = (monthly_income['доход факт'] / monthly_income['факт затраты'] * 100).fillna(0)

fig4 = make_subplots(
    rows=2, cols=1,
    subplot_titles=('Доход: План vs Факт', 'ROI: План vs Факт'),
    vertical_spacing=0.12
)

fig4.add_trace(
    go.Bar(name='Доход План', x=monthly_income['Месяц_название'], 
           y=monthly_income['доход план'], marker_color='lightseagreen'),
    row=1, col=1
)
fig4.add_trace(
    go.Bar(name='Доход Факт', x=monthly_income['Месяц_название'], 
           y=monthly_income['доход факт'], marker_color='teal'),
    row=1, col=1
)

fig4.add_trace(
    go.Scatter(name='ROI План', x=monthly_income['Месяц_название'], 
               y=monthly_income['ROI план, %'], mode='lines+markers', 
               line=dict(color='orange', width=3), showlegend=False),
    row=2, col=1
)
fig4.add_trace(
    go.Scatter(name='ROI Факт', x=monthly_income['Месяц_название'], 
               y=monthly_income['ROI факт, %'], mode='lines+markers',
               line=dict(color='darkorange', width=3), showlegend=False),
    row=2, col=1
)

fig4.update_layout(height=800, title_text="<b>Финансовые показатели</b>", 
                   barmode='group', template='plotly_white')
fig4.update_xaxes(tickangle=45)
fig4.update_yaxes(title_text="Доход, руб", row=1, col=1)
fig4.update_yaxes(title_text="ROI, %", row=2, col=1)

# 5. Анализ по группам сбыта
sales_by_group = df.groupby('группа сбыта').agg({
    'Плановые продажи, руб': 'sum',
    'Факт продажи, руб (от ЦМ)': 'sum',
    'план затарты': 'sum',
    'факт затраты': 'sum',
    'доход факт': 'sum'
}).reset_index()

fig5 = make_subplots(
    rows=1, cols=2,
    specs=[[{'type':'bar'}, {'type':'pie'}]],
    subplot_titles=('Продажи по группам сбыта', 'Распределение фактических продаж')
)

fig5.add_trace(
    go.Bar(name='План', x=sales_by_group['группа сбыта'], 
           y=sales_by_group['Плановые продажи, руб'], marker_color='skyblue'),
    row=1, col=1
)
fig5.add_trace(
    go.Bar(name='Факт', x=sales_by_group['группа сбыта'], 
           y=sales_by_group['Факт продажи, руб (от ЦМ)'], marker_color='navy'),
    row=1, col=1
)

fig5.add_trace(
    go.Pie(labels=sales_by_group['группа сбыта'], 
           values=sales_by_group['Факт продажи, руб (от ЦМ)'],
           marker=dict(colors=['#3498db', '#e74c3c'])),
    row=1, col=2
)

fig5.update_layout(height=500, title_text="<b>Анализ по группам сбыта</b>", 
                   template='plotly_white')

# 6. Топ-10 сетей по продажам
top_networks = df.groupby('Сеть').agg({
    'Факт продажи, руб (от ЦМ)': 'sum',
    'доход факт': 'sum'
}).sort_values('Факт продажи, руб (от ЦМ)', ascending=False).head(10).reset_index()

fig6 = go.Figure()
fig6.add_trace(go.Bar(
    y=top_networks['Сеть'],
    x=top_networks['Факт продажи, руб (от ЦМ)'],
    orientation='h',
    marker=dict(color=top_networks['Факт продажи, руб (от ЦМ)'], 
                colorscale='Viridis', showscale=True)
))
fig6.update_layout(
    title='<b>ТОП-10 сетей по фактическим продажам</b>',
    xaxis_title='Продажи, руб',
    yaxis_title='Сеть',
    height=500,
    template='plotly_white'
)

# 7. Воронка продаж и затрат
funnel_data = pd.DataFrame({
    'Показатель': ['План продаж', 'Факт продаж', 'План затрат', 'Факт затрат', 
                   'План дохода', 'Факт дохода'],
    'Значение': [
        kpi['plan_sales_rub'],
        kpi['fact_sales_rub'],
        kpi['plan_costs'],
        kpi['fact_costs'],
        kpi['plan_income'],
        kpi['fact_income']
    ]
})

fig7 = px.funnel(funnel_data, x='Значение', y='Показатель', 
                 color='Показатель',
                 title='<b>Финансовая воронка</b>')
fig7.update_layout(height=600, template='plotly_white')

# 8. Тепловая карта выполнения плана по месяцам и группам
heatmap_data = df.groupby(['Месяц_название', 'группа сбыта']).agg({
    'Плановые продажи, руб': 'sum',
    'Факт продажи, руб (от ЦМ)': 'sum'
}).reset_index()
heatmap_data['Выполнение, %'] = (heatmap_data['Факт продажи, руб (от ЦМ)'] / 
                                  heatmap_data['Плановые продажи, руб'] * 100).fillna(0)

heatmap_pivot = heatmap_data.pivot(index='группа сбыта', 
                                     columns='Месяц_название', 
                                     values='Выполнение, %')

fig8 = go.Figure(data=go.Heatmap(
    z=heatmap_pivot.values,
    x=heatmap_pivot.columns,
    y=heatmap_pivot.index,
    colorscale='RdYlGn',
    zmid=100,
    text=np.round(heatmap_pivot.values, 1),
    texttemplate='%{text}%',
    textfont={"size": 12},
    colorbar=dict(title="Выполнение, %")
))
fig8.update_layout(
    title='<b>Тепловая карта выполнения плана</b>',
    xaxis_title='Месяц',
    yaxis_title='Группа сбыта',
    height=400,
    template='plotly_white'
)
fig8.update_xaxes(tickangle=45)

# ============================================================================
# СОЗДАНИЕ HTML ОТЧЕТА
# ============================================================================

print("Создание HTML отчета...")

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>BI Dashboard - Анализ продаж и затрат</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 10px;
            font-size: 36px;
        }}
        .subtitle {{
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 30px;
            font-size: 16px;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 40px;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section-title {{
            color: #34495e;
            font-size: 24px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #3498db;
        }}
        .metric-row {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-box {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        .metric-label {{
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .positive {{
            color: #27ae60;
        }}
        .negative {{
            color: #e74c3c;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .chart-container {{
            margin: 30px 0;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 BI Dashboard - Анализ продаж и затрат</h1>
        <div class="subtitle">
            Период: {df['Дата'].min().strftime('%d.%m.%Y')} - {df['Дата'].max().strftime('%d.%m.%Y')} 
            | Всего записей: {len(df):,}
        </div>
        
        <!-- KPI Cards -->
        <div class="section">
            <div class="section-title">📈 Ключевые показатели</div>
            <div class="kpi-grid">
                {create_kpi_card("Продажи План (руб)", kpi['plan_sales_rub'], '', '#3498db')}
                {create_kpi_card("Продажи Факт (руб)", kpi['fact_sales_rub'], '', '#2ecc71')}
                {create_kpi_card("Выполнение плана", kpi['fulfillment_rub'], '%', '#9b59b6')}
                {create_kpi_card("Затраты План", kpi['plan_costs'], '', '#e67e22')}
                {create_kpi_card("Затраты Факт", kpi['fact_costs'], '', '#e74c3c')}
                {create_kpi_card("ROI Факт", kpi['roi_fact'], '%', '#1abc9c')}
            </div>
        </div>
        
        <!-- Detailed Metrics -->
        <div class="section">
            <div class="section-title">📊 Детальные метрики</div>
            <div class="metric-row">
                <div class="metric-box">
                    <div class="metric-label">План продаж (шт)</div>
                    <div class="metric-value">{kpi['plan_sales_units']:,.0f}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Факт продаж (шт)</div>
                    <div class="metric-value">{kpi['fact_sales_units']:,.0f}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Выполнение плана (шт)</div>
                    <div class="metric-value {'positive' if kpi['fulfillment_units'] >= 100 else 'negative'}">
                        {kpi['fulfillment_units']:.1f}%
                    </div>
                </div>
            </div>
            
            <div class="metric-row">
                <div class="metric-box">
                    <div class="metric-label">План дохода</div>
                    <div class="metric-value">{kpi['plan_income']:,.0f} ₽</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Факт дохода</div>
                    <div class="metric-value">{kpi['fact_income']:,.0f} ₽</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Отклонение дохода</div>
                    <div class="metric-value {'positive' if kpi['income_variance'] >= 0 else 'negative'}">
                        {kpi['income_variance']:,.0f} ₽ ({kpi['income_variance_pct']:.1f}%)
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Таблица затрат по категориям -->
        <div class="section">
            <div class="section-title">💰 Затраты по категориям</div>
            <table>
                <thead>
                    <tr>
                        <th>Категория</th>
                        <th>План, ₽</th>
                        <th>Факт, ₽</th>
                        <th>Отклонение, ₽</th>
                        <th>Отклонение, %</th>
                    </tr>
                </thead>
                <tbody>
"""

for _, row in costs_df.iterrows():
    color_class = 'negative' if row['Отклонение'] > 0 else 'positive'
    html_content += f"""
                    <tr>
                        <td><b>{row['Категория']}</b></td>
                        <td>{row['План']:,.0f}</td>
                        <td>{row['Факт']:,.0f}</td>
                        <td class="{color_class}">{row['Отклонение']:,.0f}</td>
                        <td class="{color_class}">{row['Отклонение, %']:.1f}%</td>
                    </tr>
"""

html_content += f"""
                </tbody>
            </table>
        </div>
        
        <!-- Графики -->
        <div class="chart-container">
            {fig1.to_html(full_html=False, include_plotlyjs='cdn')}
        </div>
        
        <div class="chart-container">
            {fig2.to_html(full_html=False, include_plotlyjs=False)}
        </div>
        
        <div class="chart-container">
            {fig8.to_html(full_html=False, include_plotlyjs=False)}
        </div>
        
        <div class="chart-container">
            {fig3.to_html(full_html=False, include_plotlyjs=False)}
        </div>
        
        <div class="chart-container">
            {fig4.to_html(full_html=False, include_plotlyjs=False)}
        </div>
        
        <div class="chart-container">
            {fig5.to_html(full_html=False, include_plotlyjs=False)}
        </div>
        
        <div class="chart-container">
            {fig6.to_html(full_html=False, include_plotlyjs=False)}
        </div>
        
        <div class="chart-container">
            {fig7.to_html(full_html=False, include_plotlyjs=False)}
        </div>
        
        <!-- Footer -->
        <div style="text-align: center; margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; color: #7f8c8d;">
            <p>📅 Отчет сгенерирован: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>
            <p>Источник данных: data.xlsx | Записей обработано: {len(df):,}</p>
        </div>
    </div>
</body>
</html>
"""

# Сохранение отчета
output_file = '/workspace/bi_dashboard_report.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n{'='*80}")
print("✅ BI Dashboard успешно создан!")
print(f"{'='*80}")
print(f"📁 Файл отчета: {output_file}")
print(f"📊 Всего графиков: 8")
print(f"📈 KPI метрик: 15+")
print(f"\n🌐 Откройте файл в браузере для просмотра интерактивного дашборда")
print(f"{'='*80}")
