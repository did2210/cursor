"""
🎯 Профессиональный BI Dashboard
Полная копия функционала со скриншотов + улучшения
Запуск: python professional_bi_dashboard.py
Открыть: http://localhost:8050
"""

import dash
from dash import dcc, html, Input, Output, dash_table, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime

print("="*80)
print("         🚀 ПРОФЕССИОНАЛЬНЫЙ BI DASHBOARD")
print("="*80)

# ============================================================================
# ЗАГРУЗКА И ПОДГОТОВКА ДАННЫХ
# ============================================================================

print("\n📂 Загрузка данных...")
import os

# Автоматически ищем data.xlsx в текущей директории
script_dir = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(script_dir, 'data.xlsx')

# ЕСЛИ НУЖЕН ДРУГОЙ ПУТЬ - РАСКОММЕНТИРУЙТЕ И УКАЖИТЕ:
# DATA_PATH = r'\\FS\Users\Private\GFD\Public\Трейд-маркетинг\7.Общие документы\Гусев\итог\data.xlsx'

if not os.path.exists(DATA_PATH):
    print(f"❌ ОШИБКА: Файл не найден: {DATA_PATH}")
    print(f"📁 Ищу в: {script_dir}")
    print("💡 Поместите data.xlsx в ту же папку что и скрипт")
    print("   ИЛИ укажите полный путь в переменной DATA_PATH")
    input("Нажмите Enter для выхода...")
    exit(1)

df = pd.read_excel(DATA_PATH)

# Подготовка данных
df['Дата'] = pd.to_datetime(df['Дата'])
df['Месяц_название'] = df['Дата'].dt.strftime('%Y-%m')
df['Год'] = df['Дата'].dt.year
df['Месяц'] = df['Дата'].dt.month
df['Квартал'] = 'Q' + df['Дата'].dt.quarter.astype(str) + ' ' + df['Год'].astype(str)

# Заполнение пропущенных значений
numeric_cols = df.select_dtypes(include=[np.number]).columns
df[numeric_cols] = df[numeric_cols].fillna(0)

print(f"✅ Загружено {len(df):,} записей")
print(f"📅 Период: {df['Дата'].min().date()} → {df['Дата'].max().date()}")

# ============================================================================
# СОЗДАНИЕ ПРИЛОЖЕНИЯ
# ============================================================================

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    title="BI Dashboard"
)

# Списки для фильтров
contracts_list = sorted([{'label': str(c), 'value': str(c)} for c in df['Контракт'].unique()], key=lambda x: x['label'])
networks_list = sorted([{'label': str(n), 'value': str(n)} for n in df['Сеть'].unique()], key=lambda x: x['label'])
brands_list = sorted([{'label': str(b), 'value': str(b)} for b in df['Brand_format'].unique()], key=lambda x: x['label'])
groups_list = sorted([{'label': str(g), 'value': str(g)} for g in df['группа сбыта'].unique()], key=lambda x: x['label'])
months_list = sorted([{'label': m, 'value': m} for m in df['Месяц_название'].unique()], key=lambda x: x['value'])

# ============================================================================
# LAYOUT
# ============================================================================

app.layout = dbc.Container([
    
    # Заголовок
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1([
                    html.I(className="fas fa-chart-line me-3"),
                    "BI Dashboard - Анализ контрактов"
                ], className="text-white mb-2"),
                html.P("Профессиональная аналитика продаж с детальной визуализацией",
                      className="text-white-50 mb-0")
            ], style={
                'background': 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
                'padding': '25px 30px',
                'borderRadius': '10px',
                'boxShadow': '0 4px 15px rgba(0,0,0,0.2)',
                'marginTop': '20px',
                'marginBottom': '25px'
            })
        ])
    ]),
    
    # Панель фильтров
    dbc.Card([
        dbc.CardHeader([
            html.H5([
                html.I(className="fas fa-filter me-2"),
                "Фильтры"
            ], className="mb-0")
        ], style={'backgroundColor': '#f8f9fa'}),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("📋 Контракт", className="fw-bold"),
                    dcc.Dropdown(
                        id='filter-contract',
                        options=[{'label': 'Все контракты', 'value': 'ALL'}] + contracts_list,
                        value='ALL',
                        placeholder="Выберите контракт...",
                        className="mb-3"
                    )
                ], md=3),
                
                dbc.Col([
                    dbc.Label("🏪 Сеть", className="fw-bold"),
                    dcc.Dropdown(
                        id='filter-network',
                        options=[{'label': 'Все сети', 'value': 'ALL'}] + networks_list,
                        value='ALL',
                        placeholder="Выберите сеть...",
                        className="mb-3"
                    )
                ], md=3),
                
                dbc.Col([
                    dbc.Label("🎯 Бренд", className="fw-bold"),
                    dcc.Dropdown(
                        id='filter-brand',
                        options=[{'label': 'Все бренды', 'value': 'ALL'}] + brands_list,
                        value='ALL',
                        placeholder="Выберите бренд...",
                        className="mb-3"
                    )
                ], md=3),
                
                dbc.Col([
                    dbc.Label("📊 Группа сбыта", className="fw-bold"),
                    dcc.Dropdown(
                        id='filter-group',
                        options=[{'label': 'Все группы', 'value': 'ALL'}] + groups_list,
                        value='ALL',
                        placeholder="Выберите группу...",
                        className="mb-3"
                    )
                ], md=3),
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("📅 Период", className="fw-bold"),
                    dcc.DatePickerRange(
                        id='filter-date',
                        start_date=df['Дата'].min(),
                        end_date=df['Дата'].max(),
                        display_format='DD.MM.YYYY',
                        className="mb-3"
                    )
                ], md=6),
                
                dbc.Col([
                    dbc.Label("📆 Месяц", className="fw-bold"),
                    dcc.Dropdown(
                        id='filter-month',
                        options=[{'label': 'Все месяцы', 'value': 'ALL'}] + months_list,
                        value='ALL',
                        placeholder="Выберите месяц...",
                        className="mb-3"
                    )
                ], md=3),
                
                dbc.Col([
                    html.Br(),
                    dbc.Button([
                        html.I(className="fas fa-redo me-2"),
                        "Сбросить"
                    ], id='btn-reset', color='danger', className="w-100")
                ], md=3)
            ])
        ])
    ], className="mb-4", style={'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'}),
    
    # Информация о выборке
    dbc.Row([
        dbc.Col([
            dbc.Alert([
                html.Div([
                    html.Span([
                        html.I(className="fas fa-database me-2"),
                        "Записей в выборке: "
                    ], className="fw-bold"),
                    html.Span(id='info-records', className="fs-5 fw-bold text-primary")
                ])
            ], color='light', className="mb-4")
        ])
    ]),
    
    # KPI Спидометры (как на скриншоте)
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='gauge-roi-plan', config={'displayModeBar': False})
                ])
            ], className="h-100")
        ], md=2),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='gauge-roi-fact', config={'displayModeBar': False})
                ])
            ], className="h-100")
        ], md=2),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='gauge-fulfillment-units', config={'displayModeBar': False})
                ])
            ], className="h-100")
        ], md=2),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='gauge-fulfillment-rub', config={'displayModeBar': False})
                ])
            ], className="h-100")
        ], md=2),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='gauge-costs', config={'displayModeBar': False})
                ])
            ], className="h-100")
        ], md=2),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='gauge-margin', config={'displayModeBar': False})
                ])
            ], className="h-100")
        ], md=2),
    ], className="mb-4"),
    
    # Графики трендов
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📊 Динамика продаж и затрат", className="fw-bold"),
                dbc.CardBody([
                    dcc.Graph(id='chart-trends', config={'displayModeBar': True})
                ])
            ])
        ], md=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("💰 Структура затрат", className="fw-bold"),
                dbc.CardBody([
                    dcc.Graph(id='chart-costs-structure', config={'displayModeBar': True})
                ])
            ])
        ], md=6),
    ], className="mb-4"),
    
    # Детальная таблица по контрактам
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-table me-2"),
                        "Детальная таблица по контрактам"
                    ], className="mb-0")
                ]),
                dbc.CardBody([
                    html.Div(id='detailed-table')
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Дополнительные графики
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("🏆 ТОП-10 контрактов", className="fw-bold"),
                dbc.CardBody([
                    dcc.Graph(id='chart-top-contracts', config={'displayModeBar': True})
                ])
            ])
        ], md=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📈 Выполнение плана по месяцам", className="fw-bold"),
                dbc.CardBody([
                    dcc.Graph(id='chart-fulfillment', config={'displayModeBar': True})
                ])
            ])
        ], md=6),
    ], className="mb-4"),
    
    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P([
                html.I(className="fas fa-info-circle me-2"),
                f"Последнее обновление данных: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            ], className="text-muted text-center")
        ])
    ])
    
], fluid=True, style={'backgroundColor': '#f5f7fa', 'paddingBottom': '30px'})

# ============================================================================
# CALLBACKS
# ============================================================================

# Сброс фильтров
@app.callback(
    [Output('filter-contract', 'value'),
     Output('filter-network', 'value'),
     Output('filter-brand', 'value'),
     Output('filter-group', 'value'),
     Output('filter-month', 'value'),
     Output('filter-date', 'start_date'),
     Output('filter-date', 'end_date')],
    [Input('btn-reset', 'n_clicks')],
    prevent_initial_call=True
)
def reset_filters(n):
    return 'ALL', 'ALL', 'ALL', 'ALL', 'ALL', df['Дата'].min(), df['Дата'].max()

# Главный callback
@app.callback(
    [Output('info-records', 'children'),
     Output('gauge-roi-plan', 'figure'),
     Output('gauge-roi-fact', 'figure'),
     Output('gauge-fulfillment-units', 'figure'),
     Output('gauge-fulfillment-rub', 'figure'),
     Output('gauge-costs', 'figure'),
     Output('gauge-margin', 'figure'),
     Output('chart-trends', 'figure'),
     Output('chart-costs-structure', 'figure'),
     Output('detailed-table', 'children'),
     Output('chart-top-contracts', 'figure'),
     Output('chart-fulfillment', 'figure')],
    [Input('filter-contract', 'value'),
     Input('filter-network', 'value'),
     Input('filter-brand', 'value'),
     Input('filter-group', 'value'),
     Input('filter-month', 'value'),
     Input('filter-date', 'start_date'),
     Input('filter-date', 'end_date')]
)
def update_dashboard(contract, network, brand, group, month, start_date, end_date):
    # Фильтрация
    filtered = df.copy()
    
    if contract != 'ALL':
        filtered = filtered[filtered['Контракт'] == contract]
    if network != 'ALL':
        filtered = filtered[filtered['Сеть'] == network]
    if brand != 'ALL':
        filtered = filtered[filtered['Brand_format'] == brand]
    if group != 'ALL':
        filtered = filtered[filtered['группа сбыта'] == group]
    if month != 'ALL':
        filtered = filtered[filtered['Месяц_название'] == month]
    if start_date and end_date:
        filtered = filtered[(filtered['Дата'] >= start_date) & (filtered['Дата'] <= end_date)]
    
    # Расчет метрик
    plan_sales_rub = filtered['Плановые продажи, руб'].sum()
    fact_sales_rub = filtered['Факт продажи, руб (от ЦМ)'].sum()
    plan_sales_units = filtered['Плановые продажи, шт'].sum()
    fact_sales_units = filtered['Факт продажи, шт.'].sum()
    plan_costs = filtered['план затарты'].sum()
    fact_costs = filtered['факт затраты'].sum()
    plan_income = filtered['доход план'].sum()
    fact_income = filtered['доход факт'].sum()
    
    fulfillment_rub = (fact_sales_rub / plan_sales_rub * 100) if plan_sales_rub > 0 else 0
    fulfillment_units = (fact_sales_units / plan_sales_units * 100) if plan_sales_units > 0 else 0
    roi_plan = (plan_income / plan_costs * 100) if plan_costs > 0 else 0
    roi_fact = (fact_income / fact_costs * 100) if fact_costs > 0 else 0
    margin = (fact_income / fact_sales_rub * 100) if fact_sales_rub > 0 else 0
    costs_percent = (fact_costs / plan_costs * 100) if plan_costs > 0 else 0
    
    # === СПИДОМЕТРЫ ===
    def create_gauge(value, title, suffix='%', color='green'):
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': title, 'font': {'size': 14}},
            number={'suffix': suffix, 'font': {'size': 20}},
            gauge={
                'axis': {'range': [0, max(150, value + 20)]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 100], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 100
                }
            }
        ))
        fig.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10))
        return fig
    
    gauge_roi_plan_fig = create_gauge(roi_plan, "ROI план", "%", "#2ecc71")
    gauge_roi_fact_fig = create_gauge(roi_fact, "ROI факт", "%", "#27ae60")
    gauge_fulfillment_units_fig = create_gauge(fulfillment_units, "Выполнение шт", "%", "#3498db")
    gauge_fulfillment_rub_fig = create_gauge(fulfillment_rub, "Выполнение руб", "%", "#2980b9")
    gauge_costs_fig = create_gauge(costs_percent, "Затраты", "%", "#e67e22")
    gauge_margin_fig = create_gauge(margin, "Маржа", "%", "#9b59b6")
    
    # === ГРАФИК ТРЕНДОВ ===
    monthly = filtered.groupby('Месяц_название').agg({
        'Плановые продажи, руб': 'sum',
        'Факт продажи, руб (от ЦМ)': 'sum',
        'факт затраты': 'sum'
    }).reset_index().sort_values('Месяц_название')
    
    fig_trends = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Продажи (млрд руб)', 'Затраты (млрд руб)'),
        vertical_spacing=0.15
    )
    
    fig_trends.add_trace(go.Scatter(
        x=monthly['Месяц_название'],
        y=monthly['Плановые продажи, руб'] / 1e9,
        name='План продаж',
        fill='tozeroy',
        line=dict(color='lightblue', width=2)
    ), row=1, col=1)
    
    fig_trends.add_trace(go.Scatter(
        x=monthly['Месяц_название'],
        y=monthly['Факт продажи, руб (от ЦМ)'] / 1e9,
        name='Факт продаж',
        fill='tonexty',
        line=dict(color='darkblue', width=3)
    ), row=1, col=1)
    
    fig_trends.add_trace(go.Bar(
        x=monthly['Месяц_название'],
        y=monthly['факт затраты'] / 1e9,
        name='Затраты',
        marker_color='#e67e22'
    ), row=2, col=1)
    
    fig_trends.update_layout(height=500, showlegend=True, template='plotly_white')
    fig_trends.update_xaxes(tickangle=45)
    
    # === СТРУКТУРА ЗАТРАТ ===
    costs_data = {
        'Листинг': filtered['Фактические затраты «Листинг/безусловные выплаты», руб'].sum(),
        'Скидка в цене': filtered['Фактические затраты «Скидка в цене», руб'].sum(),
        'Ретро': filtered['Фактические затраты «Ретро», руб'].sum(),
        'Маркетинг': filtered['Фактические затраты «Маркетинг», руб'].sum(),
        'Промо-скидка': filtered['Фактические затраты «Промо-скидка», руб'].sum()
    }
    
    fig_costs = go.Figure(data=[
        go.Pie(
            labels=list(costs_data.keys()),
            values=list(costs_data.values()),
            hole=0.4,
            marker=dict(colors=['#3498db', '#2ecc71', '#e67e22', '#9b59b6', '#e74c3c'])
        )
    ])
    fig_costs.update_layout(height=400, template='plotly_white')
    
    # === ТАБЛИЦА ===
    if contract != 'ALL':
        # Детализация по месяцам для контракта
        table_data = filtered.groupby('Месяц_название').agg({
            'Плановые продажи, руб': 'sum',
            'Факт продажи, руб (от ЦМ)': 'sum',
            'Плановые продажи, шт': 'sum',
            'Факт продажи, шт.': 'sum',
            'факт затраты': 'sum',
            'доход факт': 'sum'
        }).reset_index()
        
        table_data['Выполнение %'] = (table_data['Факт продажи, руб (от ЦМ)'] / 
                                       table_data['Плановые продажи, руб'] * 100).round(1)
        table_data['ROI %'] = (table_data['доход факт'] / 
                               table_data['факт затраты'] * 100).round(1)
        
        table_data.columns = ['Месяц', 'План продаж ₽', 'Факт продаж ₽', 
                             'План продаж шт', 'Факт продаж шт', 
                             'Затраты ₽', 'Доход ₽', 'Выполнение %', 'ROI %']
    else:
        # Таблица по контрактам
        table_data = filtered.groupby('Контракт').agg({
            'Плановые продажи, руб': 'sum',
            'Факт продажи, руб (от ЦМ)': 'sum',
            'факт затраты': 'sum',
            'доход факт': 'sum'
        }).reset_index()
        
        table_data['Выполнение %'] = (table_data['Факт продажи, руб (от ЦМ)'] / 
                                       table_data['Плановые продажи, руб'] * 100).round(1)
        table_data['ROI %'] = (table_data['доход факт'] / 
                               table_data['факт затраты'] * 100).round(1)
        
        table_data = table_data.nlargest(20, 'Факт продажи, руб (от ЦМ)')
        table_data.columns = ['Контракт', 'План ₽', 'Факт ₽', 
                             'Затраты ₽', 'Доход ₽', 'Выполнение %', 'ROI %']
    
    # Форматирование чисел
    for col in table_data.columns:
        if '₽' in col:
            table_data[col] = table_data[col].apply(lambda x: f"{x:,.0f}".replace(',', ' '))
    
    table_component = dash_table.DataTable(
        data=table_data.to_dict('records'),
        columns=[{'name': c, 'id': c} for c in table_data.columns],
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'fontFamily': 'Arial'
        },
        style_header={
            'backgroundColor': '#1e3c72',
            'color': 'white',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'column_id': 'Выполнение %'},
                'backgroundColor': '#d4edda',
                'fontWeight': 'bold'
            },
            {
                'if': {'column_id': 'ROI %'},
                'backgroundColor': '#fff3cd',
                'fontWeight': 'bold'
            }
        ],
        page_size=15
    )
    
    # === ТОП-10 КОНТРАКТОВ ===
    top_contracts = filtered.groupby('Контракт')['Факт продажи, руб (от ЦМ)'].sum().nlargest(10)
    
    fig_top = go.Figure(go.Bar(
        y=top_contracts.index,
        x=top_contracts.values / 1e9,
        orientation='h',
        marker=dict(
            color=top_contracts.values,
            colorscale='Viridis',
            showscale=True
        )
    ))
    fig_top.update_layout(
        xaxis_title='Продажи, млрд руб',
        yaxis_title='',
        height=400,
        template='plotly_white'
    )
    
    # === ВЫПОЛНЕНИЕ ПЛАНА ===
    monthly['Выполнение %'] = (monthly['Факт продажи, руб (от ЦМ)'] / 
                               monthly['Плановые продажи, руб'] * 100).fillna(0)
    
    fig_fulfillment = go.Figure()
    fig_fulfillment.add_trace(go.Scatter(
        x=monthly['Месяц_название'],
        y=monthly['Выполнение %'],
        mode='lines+markers',
        line=dict(width=3, color='#3498db'),
        marker=dict(size=10)
    ))
    fig_fulfillment.add_hline(y=100, line_dash="dash", line_color="red", 
                             annotation_text="Цель 100%")
    fig_fulfillment.update_layout(
        yaxis_title='Выполнение плана, %',
        height=400,
        template='plotly_white'
    )
    fig_fulfillment.update_xaxes(tickangle=45)
    
    return (
        f"{len(filtered):,}",
        gauge_roi_plan_fig,
        gauge_roi_fact_fig,
        gauge_fulfillment_units_fig,
        gauge_fulfillment_rub_fig,
        gauge_costs_fig,
        gauge_margin_fig,
        fig_trends,
        fig_costs,
        table_component,
        fig_top,
        fig_fulfillment
    )

# ============================================================================
# ЗАПУСК СЕРВЕРА
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("✅ СЕРВЕР ЗАПУЩЕН!")
    print("="*80)
    print("\n🌐 Откройте в браузере:")
    print("   http://localhost:8050")
    print("\n📊 Функционал:")
    print("   ✓ Фильтры по всем параметрам")
    print("   ✓ 6 спидометров с KPI")
    print("   ✓ Графики трендов")
    print("   ✓ Детальная таблица")
    print("   ✓ ТОП контрактов")
    print("\n💡 Для остановки нажмите Ctrl+C")
    print("="*80 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=8050)
