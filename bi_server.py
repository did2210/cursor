"""
🎯 BI Dashboard - Локальный веб-сервер
Запуск: python bi_server.py
Откройте в браузере: http://localhost:8050
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime

print("="*80)
print("         🚀 ЗАПУСК BI DASHBOARD СЕРВЕРА")
print("="*80)

# Загрузка данных
print("\n📂 Загрузка данных...")
import os

# Автоматически ищем data.xlsx в текущей директории
script_dir = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(script_dir, 'data.xlsx')

# ЕСЛИ НУЖЕН ДРУГОЙ ПУТЬ - РАСКОММЕНТИРУЙТЕ И УКАЖИТЕ:
# DATA_PATH = r'\\FS\Users\Private\GFD\Public\Трейд-маркетинг\7.Общие документы\Гусев\итог\data.xlsx'

if not os.path.exists(DATA_PATH):
    print(f"❌ ОШИБКА: Файл не найден: {DATA_PATH}")
    print("💡 Укажите правильный путь в переменной DATA_PATH")
    input("Нажмите Enter для выхода...")
    exit(1)

df = pd.read_excel(DATA_PATH)

# Подготовка данных
df['Дата'] = pd.to_datetime(df['Дата'])
df['Месяц_название'] = df['Дата'].dt.strftime('%Y-%m')
df['Год'] = df['Дата'].dt.year
df['Месяц'] = df['Дата'].dt.month

# Заполнение пропущенных значений
numeric_cols = df.select_dtypes(include=[np.number]).columns
df[numeric_cols] = df[numeric_cols].fillna(0)

print(f"✅ Загружено {len(df):,} записей")
print(f"📅 Период: {df['Дата'].min().date()} → {df['Дата'].max().date()}")
print(f"📊 Контрактов: {df['Контракт'].nunique()}")
print(f"🏪 Сетей: {df['Сеть'].nunique()}")
print(f"🎯 Брендов: {df['Brand_format'].nunique()}")

# Создание приложения Dash
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.LUX],
    suppress_callback_exceptions=True
)

app.title = "📊 BI Dashboard"

# Получение уникальных значений для фильтров
contracts = sorted([{'label': str(c), 'value': str(c)} for c in df['Контракт'].unique()], key=lambda x: x['label'])
networks = sorted([{'label': str(n), 'value': str(n)} for n in df['Сеть'].unique()], key=lambda x: x['label'])
brands = sorted([{'label': str(b), 'value': str(b)} for b in df['Brand_format'].unique()], key=lambda x: x['label'])
groups = sorted([{'label': str(g), 'value': str(g)} for g in df['группа сбыта'].unique()], key=lambda x: x['label'])
years = sorted([{'label': str(y), 'value': y} for y in df['Год'].unique()], key=lambda x: x['value'])

# Определение стилей
CARD_STYLE = {
    'textAlign': 'center',
    'padding': '20px',
    'borderRadius': '10px',
    'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
    'marginBottom': '10px',
    'height': '120px'
}

# Layout приложения
app.layout = dbc.Container([
    # Заголовок
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("📊 BI Dashboard - Анализ продаж", 
                       style={'color': 'white', 'marginBottom': '10px'}),
                html.P("Интерактивный анализ с фильтрами по контрактам, датам и метрикам",
                      style={'color': 'white', 'fontSize': '16px'})
            ], style={
                'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'padding': '30px',
                'borderRadius': '10px',
                'marginBottom': '20px',
                'marginTop': '20px'
            })
        ])
    ]),
    
    # Панель фильтров
    dbc.Card([
        dbc.CardHeader(html.H4("🔍 Фильтры", style={'margin': 0})),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("📋 Контракт:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='contract-filter',
                        options=[{'label': 'Все контракты', 'value': 'ALL'}] + contracts,
                        value='ALL',
                        placeholder="Выберите контракт...",
                        style={'marginBottom': '15px'}
                    )
                ], md=3),
                
                dbc.Col([
                    html.Label("🏪 Сеть:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='network-filter',
                        options=[{'label': 'Все сети', 'value': 'ALL'}] + networks,
                        value='ALL',
                        placeholder="Выберите сеть...",
                        style={'marginBottom': '15px'}
                    )
                ], md=3),
                
                dbc.Col([
                    html.Label("🎯 Бренд:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='brand-filter',
                        options=[{'label': 'Все бренды', 'value': 'ALL'}] + brands,
                        value='ALL',
                        placeholder="Выберите бренд...",
                        style={'marginBottom': '15px'}
                    )
                ], md=3),
                
                dbc.Col([
                    html.Label("📊 Группа сбыта:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='group-filter',
                        options=[{'label': 'Все группы', 'value': 'ALL'}] + groups,
                        value='ALL',
                        placeholder="Выберите группу...",
                        style={'marginBottom': '15px'}
                    )
                ], md=3),
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.Label("📅 Период:", style={'fontWeight': 'bold'}),
                    dcc.DatePickerRange(
                        id='date-filter',
                        start_date=df['Дата'].min(),
                        end_date=df['Дата'].max(),
                        display_format='YYYY-MM-DD',
                        style={'marginBottom': '15px'}
                    )
                ], md=6),
                
                dbc.Col([
                    html.Label("🗓️ Год:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='year-filter',
                        options=[{'label': 'Все годы', 'value': 'ALL'}] + years,
                        value='ALL',
                        placeholder="Выберите год...",
                        style={'marginBottom': '15px'}
                    )
                ], md=3),
                
                dbc.Col([
                    html.Br(),
                    dbc.Button("🔄 Сбросить фильтры", id='reset-btn', color='danger', 
                              style={'width': '100%'})
                ], md=3)
            ])
        ])
    ], style={'marginBottom': '20px'}),
    
    # Информационный баннер
    dbc.Row([
        dbc.Col([
            dbc.Alert([
                html.H5("📊 Отображаемых записей:", style={'display': 'inline', 'marginRight': '10px'}),
                html.Span(id='record-count', style={'fontSize': '24px', 'fontWeight': 'bold'})
            ], color='info')
        ])
    ], style={'marginBottom': '20px'}),
    
    # KPI карточки
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("💰 Продажи План", style={'color': '#3498db'}),
                    html.H3(id='kpi-plan-sales', style={'color': '#2c3e50'}),
                    html.P("млрд руб", style={'color': '#7f8c8d', 'fontSize': '12px'})
                ])
            ], style={**CARD_STYLE, 'borderLeft': '5px solid #3498db'})
        ], md=2),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("✅ Продажи Факт", style={'color': '#2ecc71'}),
                    html.H3(id='kpi-fact-sales', style={'color': '#2c3e50'}),
                    html.P("млрд руб", style={'color': '#7f8c8d', 'fontSize': '12px'})
                ])
            ], style={**CARD_STYLE, 'borderLeft': '5px solid #2ecc71'})
        ], md=2),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("📈 Выполнение", style={'color': '#9b59b6'}),
                    html.H3(id='kpi-fulfillment', style={'color': '#2c3e50'}),
                    html.P("процентов", style={'color': '#7f8c8d', 'fontSize': '12px'})
                ])
            ], style={**CARD_STYLE, 'borderLeft': '5px solid #9b59b6'})
        ], md=2),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("💸 Затраты", style={'color': '#e67e22'}),
                    html.H3(id='kpi-costs', style={'color': '#2c3e50'}),
                    html.P("млрд руб", style={'color': '#7f8c8d', 'fontSize': '12px'})
                ])
            ], style={**CARD_STYLE, 'borderLeft': '5px solid #e67e22'})
        ], md=2),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("💎 Доход", style={'color': '#1abc9c'}),
                    html.H3(id='kpi-income', style={'color': '#2c3e50'}),
                    html.P("млрд руб", style={'color': '#7f8c8d', 'fontSize': '12px'})
                ])
            ], style={**CARD_STYLE, 'borderLeft': '5px solid #1abc9c'})
        ], md=2),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("🎯 ROI", style={'color': '#e74c3c'}),
                    html.H3(id='kpi-roi', style={'color': '#2c3e50'}),
                    html.P("процентов", style={'color': '#7f8c8d', 'fontSize': '12px'})
                ])
            ], style={**CARD_STYLE, 'borderLeft': '5px solid #e74c3c'})
        ], md=2),
    ], style={'marginBottom': '20px'}),
    
    # Графики
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("📊 Продажи: План vs Факт по месяцам")),
                dbc.CardBody([dcc.Graph(id='sales-chart')])
            ], style={'marginBottom': '20px'})
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("📈 Выполнение плана по месяцам")),
                dbc.CardBody([dcc.Graph(id='fulfillment-chart')])
            ], style={'marginBottom': '20px'})
        ], md=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("🎯 ROI по месяцам")),
                dbc.CardBody([dcc.Graph(id='roi-chart')])
            ], style={'marginBottom': '20px'})
        ], md=6),
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("💰 Финансовые показатели")),
                dbc.CardBody([dcc.Graph(id='financial-chart')])
            ], style={'marginBottom': '20px'})
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("🏆 ТОП-10 по выбранным фильтрам")),
                dbc.CardBody([dcc.Graph(id='top-chart')])
            ], style={'marginBottom': '20px'})
        ])
    ]),
    
], fluid=True, style={'backgroundColor': '#f8f9fa'})

# Callback для сброса фильтров
@app.callback(
    [Output('contract-filter', 'value'),
     Output('network-filter', 'value'),
     Output('brand-filter', 'value'),
     Output('group-filter', 'value'),
     Output('year-filter', 'value'),
     Output('date-filter', 'start_date'),
     Output('date-filter', 'end_date')],
    [Input('reset-btn', 'n_clicks')],
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    return 'ALL', 'ALL', 'ALL', 'ALL', 'ALL', df['Дата'].min(), df['Дата'].max()

# Главный callback для обновления всех графиков и метрик
@app.callback(
    [Output('record-count', 'children'),
     Output('kpi-plan-sales', 'children'),
     Output('kpi-fact-sales', 'children'),
     Output('kpi-fulfillment', 'children'),
     Output('kpi-costs', 'children'),
     Output('kpi-income', 'children'),
     Output('kpi-roi', 'children'),
     Output('sales-chart', 'figure'),
     Output('fulfillment-chart', 'figure'),
     Output('roi-chart', 'figure'),
     Output('financial-chart', 'figure'),
     Output('top-chart', 'figure')],
    [Input('contract-filter', 'value'),
     Input('network-filter', 'value'),
     Input('brand-filter', 'value'),
     Input('group-filter', 'value'),
     Input('year-filter', 'value'),
     Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date')]
)
def update_dashboard(contract, network, brand, group, year, start_date, end_date):
    # Фильтрация данных
    filtered_df = df.copy()
    
    if contract != 'ALL':
        filtered_df = filtered_df[filtered_df['Контракт'] == contract]
    if network != 'ALL':
        filtered_df = filtered_df[filtered_df['Сеть'] == network]
    if brand != 'ALL':
        filtered_df = filtered_df[filtered_df['Brand_format'] == brand]
    if group != 'ALL':
        filtered_df = filtered_df[filtered_df['группа сбыта'] == group]
    if year != 'ALL':
        filtered_df = filtered_df[filtered_df['Год'] == year]
    if start_date and end_date:
        filtered_df = filtered_df[(filtered_df['Дата'] >= start_date) & (filtered_df['Дата'] <= end_date)]
    
    # Расчет KPI
    plan_sales = filtered_df['Плановые продажи, руб'].sum()
    fact_sales = filtered_df['Факт продажи, руб (от ЦМ)'].sum()
    costs = filtered_df['факт затраты'].sum()
    income = filtered_df['доход факт'].sum()
    
    fulfillment = (fact_sales / plan_sales * 100) if plan_sales > 0 else 0
    roi = (income / costs * 100) if costs > 0 else 0
    
    # Подготовка данных по месяцам
    monthly = filtered_df.groupby('Месяц_название').agg({
        'Плановые продажи, руб': 'sum',
        'Факт продажи, руб (от ЦМ)': 'sum',
        'факт затраты': 'sum',
        'доход факт': 'sum'
    }).reset_index().sort_values('Месяц_название')
    
    # График продаж
    fig_sales = go.Figure()
    fig_sales.add_trace(go.Bar(
        x=monthly['Месяц_название'],
        y=monthly['Плановые продажи, руб'] / 1e9,
        name='План',
        marker_color='#3498db'
    ))
    fig_sales.add_trace(go.Bar(
        x=monthly['Месяц_название'],
        y=monthly['Факт продажи, руб (от ЦМ)'] / 1e9,
        name='Факт',
        marker_color='#2ecc71'
    ))
    fig_sales.update_layout(
        barmode='group',
        xaxis_title='Месяц',
        yaxis_title='Продажи, млрд руб',
        height=400,
        template='plotly_white'
    )
    
    # График выполнения плана
    monthly['fulfillment'] = (monthly['Факт продажи, руб (от ЦМ)'] / 
                              monthly['Плановые продажи, руб'] * 100).fillna(0)
    
    fig_fulfillment = go.Figure()
    fig_fulfillment.add_trace(go.Scatter(
        x=monthly['Месяц_название'],
        y=monthly['fulfillment'],
        mode='lines+markers',
        marker=dict(size=10, color='#9b59b6'),
        line=dict(width=3, color='#9b59b6')
    ))
    fig_fulfillment.add_hline(y=100, line_dash="dash", line_color="red", 
                             annotation_text="Цель 100%")
    fig_fulfillment.update_layout(
        xaxis_title='Месяц',
        yaxis_title='Выполнение, %',
        height=400,
        template='plotly_white'
    )
    
    # График ROI
    monthly['roi'] = (monthly['доход факт'] / monthly['факт затраты'] * 100).fillna(0)
    
    fig_roi = go.Figure()
    fig_roi.add_trace(go.Scatter(
        x=monthly['Месяц_название'],
        y=monthly['roi'],
        mode='lines+markers',
        fill='tozeroy',
        marker=dict(size=10, color='#e74c3c'),
        line=dict(width=3, color='#e74c3c')
    ))
    fig_roi.update_layout(
        xaxis_title='Месяц',
        yaxis_title='ROI, %',
        height=400,
        template='plotly_white'
    )
    
    # График финансов
    fig_financial = go.Figure()
    fig_financial.add_trace(go.Bar(
        x=monthly['Месяц_название'],
        y=monthly['факт затраты'] / 1e9,
        name='Затраты',
        marker_color='#e67e22'
    ))
    fig_financial.add_trace(go.Bar(
        x=monthly['Месяц_название'],
        y=monthly['доход факт'] / 1e9,
        name='Доход',
        marker_color='#1abc9c'
    ))
    fig_financial.update_layout(
        barmode='group',
        xaxis_title='Месяц',
        yaxis_title='Сумма, млрд руб',
        height=400,
        template='plotly_white'
    )
    
    # ТОП-10 (если выбран контракт - показываем по месяцам, иначе - по контрактам)
    if contract != 'ALL':
        # ТОП по месяцам для выбранного контракта
        top_data = monthly.nlargest(10, 'Факт продажи, руб (от ЦМ)')
        fig_top = go.Figure()
        fig_top.add_trace(go.Bar(
            y=top_data['Месяц_название'],
            x=top_data['Факт продажи, руб (от ЦМ)'] / 1e6,
            orientation='h',
            marker=dict(color=top_data['Факт продажи, руб (от ЦМ)'], 
                       colorscale='Viridis', showscale=True)
        ))
        fig_top.update_layout(
            xaxis_title='Продажи, млн руб',
            yaxis_title='Месяц',
            height=400,
            template='plotly_white'
        )
    else:
        # ТОП-10 контрактов
        top_contracts = filtered_df.groupby('Контракт')['Факт продажи, руб (от ЦМ)'].sum().nlargest(10)
        fig_top = go.Figure()
        fig_top.add_trace(go.Bar(
            y=top_contracts.index,
            x=top_contracts.values / 1e9,
            orientation='h',
            marker=dict(color=top_contracts.values, colorscale='Viridis', showscale=True)
        ))
        fig_top.update_layout(
            xaxis_title='Продажи, млрд руб',
            yaxis_title='Контракт',
            height=400,
            template='plotly_white'
        )
    
    return (
        f"{len(filtered_df):,}",
        f"{plan_sales / 1e9:.2f}",
        f"{fact_sales / 1e9:.2f}",
        f"{fulfillment:.1f}%",
        f"{costs / 1e9:.2f}",
        f"{income / 1e9:.2f}",
        f"{roi:.1f}%",
        fig_sales,
        fig_fulfillment,
        fig_roi,
        fig_financial,
        fig_top
    )

if __name__ == '__main__':
    print("\n" + "="*80)
    print("✅ СЕРВЕР ЗАПУЩЕН!")
    print("="*80)
    print("\n🌐 Откройте в браузере:")
    print("   http://localhost:8050")
    print("\n💡 Для остановки нажмите Ctrl+C")
    print("="*80 + "\n")
    
    app.run_server(debug=False, host='0.0.0.0', port=8050)
