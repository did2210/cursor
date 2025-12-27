#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BI Dashboard для анализа продаж - Расширенная версия
С фильтрами по контрактам и детализацией до SKU
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
from datetime import datetime
import numpy as np
import os

# Загрузка данных
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
    
    df['Выполнение плана дохода, %'] = np.where(
        df['доход план'] != 0,
        (df['доход факт'] / df['доход план'] * 100),
        0
    )
    
    return df

# Инициализация приложения
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "BI Dashboard - Детальный анализ по контрактам"

# Загружаем данные
df = load_data()

# Стили
CARD_STYLE = {
    'box-shadow': '0 4px 6px 0 rgba(0, 0, 0, 0.18)',
    'margin-bottom': '20px',
    'border-radius': '10px',
    'padding': '20px'
}

# Layout приложения
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("📊 BI Dashboard - Детальный анализ по контрактам и SKU", 
                   style={'textAlign': 'center', 'margin': '30px', 'color': '#2c3e50'}),
            html.Hr()
        ])
    ]),
    
    # Фильтры
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("🔍 Фильтры", className="card-title"),
                    html.Label("Выберите контракт:", style={'fontWeight': 'bold', 'marginTop': '10px'}),
                    dcc.Dropdown(
                        id='contract-dropdown',
                        options=[{'label': 'ВСЕ КОНТРАКТЫ', 'value': 'ALL'}] + 
                                [{'label': contract, 'value': contract} 
                                 for contract in sorted(df['Контракт'].unique())],
                        value='ALL',
                        clearable=False,
                        style={'marginBottom': '15px'}
                    ),
                    html.Label("Выберите сеть:", style={'fontWeight': 'bold', 'marginTop': '10px'}),
                    dcc.Dropdown(
                        id='network-dropdown',
                        options=[{'label': 'ВСЕ СЕТИ', 'value': 'ALL'}] + 
                                [{'label': network, 'value': network} 
                                 for network in sorted(df['Сеть'].unique())],
                        value='ALL',
                        clearable=False,
                        style={'marginBottom': '15px'}
                    ),
                    html.Label("Выберите SKU (Brand_format):", style={'fontWeight': 'bold', 'marginTop': '10px'}),
                    dcc.Dropdown(
                        id='sku-dropdown',
                        options=[{'label': 'ВСЕ SKU', 'value': 'ALL'}] + 
                                [{'label': sku, 'value': sku} 
                                 for sku in sorted(df['Brand_format'].unique())],
                        value='ALL',
                        clearable=False,
                        style={'marginBottom': '15px'}
                    ),
                ])
            ], style=CARD_STYLE)
        ], width=12)
    ]),
    
    # Информация о контракте
    html.Div(id='contract-info'),
    
    html.Br(),
    
    # KPI карточки
    html.Div(id='kpi-cards'),
    
    html.Br(),
    
    # График план/факт по месяцам
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='plan-fact-chart')
        ], width=12)
    ]),
    
    html.Br(),
    
    # Затраты детально
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='costs-detail-chart')
        ], width=6),
        dbc.Col([
            dcc.Graph(id='income-chart')
        ], width=6)
    ]),
    
    html.Br(),
    
    # Детальная таблица по SKU
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("📊 Детальная разбивка по SKU", className="card-title"),
                    html.Div(id='sku-table')
                ])
            ], style=CARD_STYLE)
        ], width=12)
    ]),
    
    html.Br(),
    
    # График по SKU
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='sku-chart')
        ], width=12)
    ]),
    
    html.Br(),
    html.Hr(),
    
    html.Footer([
        html.P(f"Последнее обновление: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
               style={'textAlign': 'center', 'color': 'gray'})
    ])
    
], fluid=True, style={'backgroundColor': '#f8f9fa'})

# Callback для обновления данных на основе фильтров
@app.callback(
    [Output('contract-info', 'children'),
     Output('kpi-cards', 'children'),
     Output('plan-fact-chart', 'figure'),
     Output('costs-detail-chart', 'figure'),
     Output('income-chart', 'figure'),
     Output('sku-table', 'children'),
     Output('sku-chart', 'figure')],
    [Input('contract-dropdown', 'value'),
     Input('network-dropdown', 'value'),
     Input('sku-dropdown', 'value')]
)
def update_dashboard(selected_contract, selected_network, selected_sku):
    # Фильтрация данных
    filtered_df = df.copy()
    
    if selected_contract != 'ALL':
        filtered_df = filtered_df[filtered_df['Контракт'] == selected_contract]
    
    if selected_network != 'ALL':
        filtered_df = filtered_df[filtered_df['Сеть'] == selected_network]
    
    if selected_sku != 'ALL':
        filtered_df = filtered_df[filtered_df['Brand_format'] == selected_sku]
    
    # Информация о контракте
    contract_info = create_contract_info(filtered_df, selected_contract)
    
    # KPI карточки
    kpi_cards = create_kpi_cards(filtered_df)
    
    # График план/факт
    plan_fact_fig = create_plan_fact_chart(filtered_df)
    
    # График затрат детально
    costs_fig = create_costs_detail_chart(filtered_df)
    
    # График доходов
    income_fig = create_income_chart(filtered_df)
    
    # Таблица SKU
    sku_table = create_sku_table(filtered_df)
    
    # График по SKU
    sku_chart = create_sku_chart(filtered_df)
    
    return contract_info, kpi_cards, plan_fact_fig, costs_fig, income_fig, sku_table, sku_chart

def create_contract_info(filtered_df, selected_contract):
    """Создает информацию о контракте"""
    if selected_contract == 'ALL' or filtered_df.empty:
        return dbc.Alert("Выберите контракт для просмотра детальной информации", color="info")
    
    # Получаем даты контракта
    contract_data = filtered_df[filtered_df['Контракт'] == selected_contract].iloc[0]
    start_date = contract_data['начало_контракта']
    end_date = contract_data['конец_контракта']
    network = contract_data['Сеть']
    status = contract_data['контракт2']
    
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4(f"📄 {selected_contract}", style={'color': '#2c3e50'}),
                ], width=12)
            ]),
            dbc.Row([
                dbc.Col([
                    html.P([
                        html.Strong("🏪 Сеть: "), f"{network}"
                    ], style={'fontSize': '16px', 'marginBottom': '5px'}),
                    html.P([
                        html.Strong("📅 Начало контракта: "), 
                        f"{start_date.strftime('%d.%m.%Y') if pd.notna(start_date) else 'Н/Д'}"
                    ], style={'fontSize': '16px', 'marginBottom': '5px'}),
                    html.P([
                        html.Strong("📅 Конец контракта: "), 
                        f"{end_date.strftime('%d.%m.%Y') if pd.notna(end_date) else 'Н/Д'}"
                    ], style={'fontSize': '16px', 'marginBottom': '5px'}),
                    html.P([
                        html.Strong("📊 Статус: "), 
                        html.Span(status, style={
                            'backgroundColor': '#28a745' if status == 'действующий' else '#dc3545',
                            'color': 'white',
                            'padding': '5px 10px',
                            'borderRadius': '5px',
                            'fontWeight': 'bold'
                        })
                    ], style={'fontSize': '16px', 'marginBottom': '5px'}),
                ], width=12)
            ])
        ])
    ], style=CARD_STYLE, color="light")

def create_kpi_cards(filtered_df):
    """Создает KPI карточки"""
    if filtered_df.empty:
        return dbc.Alert("Нет данных для отображения", color="warning")
    
    # Расчет метрик
    total_plan_sales = filtered_df['Плановые продажи, руб'].sum()
    total_fact_sales = filtered_df['Факт продажи, руб (от ЦМ)'].sum()
    plan_execution = (total_fact_sales / total_plan_sales * 100) if total_plan_sales > 0 else 0
    
    total_plan_income = filtered_df['доход план'].sum()
    total_fact_income = filtered_df['доход факт'].sum()
    
    total_plan_costs = filtered_df['план затарты'].sum()
    total_fact_costs = filtered_df['факт затраты'].sum()
    
    # Детализация затрат
    costs_listing = filtered_df['Фактические затраты «Листинг/безусловные выплаты», руб'].sum()
    costs_discount = filtered_df['Фактические затраты «Скидка в цене», руб'].sum()
    costs_retro = filtered_df['Фактические затраты «Ретро», руб'].sum()
    costs_marketing = filtered_df['Фактические затраты «Маркетинг», руб'].sum()
    costs_promo = filtered_df['Фактические затраты «Промо-скидка», руб'].sum()
    
    cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("💰 Продажи", className="card-title"),
                    html.H3(f"{total_fact_sales:,.0f} ₽", style={'color': '#1f77b4'}),
                    html.P(f"План: {total_plan_sales:,.0f} ₽"),
                    html.H6(f"{plan_execution:.1f}% выполнения", 
                           style={'color': 'green' if plan_execution >= 100 else 'red'})
                ])
            ], style=CARD_STYLE)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("💵 Доход", className="card-title"),
                    html.H3(f"{total_fact_income:,.0f} ₽", style={'color': '#2ca02c'}),
                    html.P(f"План: {total_plan_income:,.0f} ₽"),
                    html.H6(f"{(total_fact_income/total_plan_income*100):.1f}% выполнения"
                           if total_plan_income > 0 else "N/A",
                           style={'color': 'green' if total_fact_income >= total_plan_income else 'orange'})
                ])
            ], style=CARD_STYLE)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("💸 Затраты общие", className="card-title"),
                    html.H3(f"{total_fact_costs:,.0f} ₽", style={'color': '#d62728'}),
                    html.P(f"План: {total_plan_costs:,.0f} ₽"),
                    html.H6(f"{(total_fact_costs/total_plan_costs*100):.1f}% от плана"
                           if total_plan_costs > 0 else "N/A",
                           style={'color': 'orange'})
                ])
            ], style=CARD_STYLE)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📊 Рентабельность", className="card-title"),
                    html.H3(f"{(total_fact_income/total_fact_sales*100):.1f}%"
                           if total_fact_sales > 0 else "N/A",
                           style={'color': '#9467bd'}),
                    html.P(f"Доход / Продажи"),
                    html.H6(f"Затраты: {(total_fact_costs/total_fact_sales*100):.1f}%"
                           if total_fact_sales > 0 else "N/A",
                           style={'color': 'gray'})
                ])
            ], style=CARD_STYLE)
        ], width=3),
    ])
    
    # Детальные карточки затрат
    costs_details = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Листинг", style={'marginBottom': '5px'}),
                    html.H5(f"{costs_listing:,.0f} ₽", style={'color': '#ff7f0e'})
                ])
            ], style={'padding': '15px', 'marginBottom': '10px'})
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Скидка в цене", style={'marginBottom': '5px'}),
                    html.H5(f"{costs_discount:,.0f} ₽", style={'color': '#2ca02c'})
                ])
            ], style={'padding': '15px', 'marginBottom': '10px'})
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Ретро", style={'marginBottom': '5px'}),
                    html.H5(f"{costs_retro:,.0f} ₽", style={'color': '#d62728'})
                ])
            ], style={'padding': '15px', 'marginBottom': '10px'})
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Маркетинг", style={'marginBottom': '5px'}),
                    html.H5(f"{costs_marketing:,.0f} ₽", style={'color': '#9467bd'})
                ])
            ], style={'padding': '15px', 'marginBottom': '10px'})
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Промо-скидка", style={'marginBottom': '5px'}),
                    html.H5(f"{costs_promo:,.0f} ₽", style={'color': '#8c564b'})
                ])
            ], style={'padding': '15px', 'marginBottom': '10px'})
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Фонды", style={'marginBottom': '5px'}),
                    html.H5(f"{filtered_df['фонды'].sum():,.0f} ₽", style={'color': '#e377c2'})
                ])
            ], style={'padding': '15px', 'marginBottom': '10px'})
        ], width=2),
    ], style={'marginTop': '20px'})
    
    return html.Div([cards, costs_details])

def create_plan_fact_chart(filtered_df):
    """График план/факт по месяцам"""
    monthly_data = filtered_df.groupby('Дата').agg({
        'Плановые продажи, руб': 'sum',
        'Факт продажи, руб (от ЦМ)': 'sum'
    }).reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=monthly_data['Дата'],
        y=monthly_data['Плановые продажи, руб'],
        name='План продажи',
        line=dict(color='lightblue', width=2, dash='dash'),
        mode='lines+markers'
    ))
    
    fig.add_trace(go.Scatter(
        x=monthly_data['Дата'],
        y=monthly_data['Факт продажи, руб (от ЦМ)'],
        name='Факт продажи',
        line=dict(color='darkblue', width=3),
        mode='lines+markers',
        fill='tonexty'
    ))
    
    fig.update_layout(
        title='План/Факт продаж по месяцам',
        xaxis_title='Месяц',
        yaxis_title='Продажи, руб',
        height=400,
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

def create_costs_detail_chart(filtered_df):
    """График детальных затрат"""
    costs_data = {
        'Тип затрат': [
            'Листинг',
            'Скидка в цене',
            'Ретро',
            'Маркетинг',
            'Промо-скидка'
        ],
        'План': [
            filtered_df['Плановые затраты «Листинг/безусловные выплаты», руб'].sum(),
            filtered_df['Плановые затраты «Скидка в цене», руб'].sum(),
            filtered_df['Плановые затраты «Ретро», руб'].sum(),
            filtered_df['Плановые затраты «Маркетинг», руб'].sum(),
            filtered_df['Плановые затраты «Промо-скидка», руб'].sum()
        ],
        'Факт': [
            filtered_df['Фактические затраты «Листинг/безусловные выплаты», руб'].sum(),
            filtered_df['Фактические затраты «Скидка в цене», руб'].sum(),
            filtered_df['Фактические затраты «Ретро», руб'].sum(),
            filtered_df['Фактические затраты «Маркетинг», руб'].sum(),
            filtered_df['Фактические затраты «Промо-скидка», руб'].sum()
        ]
    }
    
    costs_df = pd.DataFrame(costs_data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=costs_df['Тип затрат'],
        y=costs_df['План'],
        name='План',
        marker_color='lightcoral'
    ))
    
    fig.add_trace(go.Bar(
        x=costs_df['Тип затрат'],
        y=costs_df['Факт'],
        name='Факт',
        marker_color='darkred'
    ))
    
    fig.update_layout(
        title='Детализация затрат по типам',
        xaxis_title='Тип затрат',
        yaxis_title='Сумма, руб',
        barmode='group',
        height=400,
        template='plotly_white'
    )
    
    return fig

def create_income_chart(filtered_df):
    """График доходов и рентабельности"""
    monthly_data = filtered_df.groupby('Дата').agg({
        'доход план': 'sum',
        'доход факт': 'sum',
        'Факт продажи, руб (от ЦМ)': 'sum'
    }).reset_index()
    
    monthly_data['Рентабельность, %'] = (
        monthly_data['доход факт'] / monthly_data['Факт продажи, руб (от ЦМ)'] * 100
    )
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Bar(x=monthly_data['Дата'], y=monthly_data['доход факт'],
               name='Доход факт', marker_color='lightgreen'),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=monthly_data['Дата'], y=monthly_data['Рентабельность, %'],
                   name='Рентабельность, %', line=dict(color='blue', width=3),
                   mode='lines+markers'),
        secondary_y=True
    )
    
    fig.update_layout(
        title='Доход и рентабельность по месяцам',
        height=400,
        template='plotly_white',
        hovermode='x unified'
    )
    
    fig.update_xaxes(title_text="Месяц")
    fig.update_yaxes(title_text="Доход, руб", secondary_y=False)
    fig.update_yaxes(title_text="Рентабельность, %", secondary_y=True)
    
    return fig

def create_sku_table(filtered_df):
    """Создает детальную таблицу по SKU"""
    if filtered_df.empty:
        return html.P("Нет данных для отображения")
    
    # Группируем по SKU
    sku_data = filtered_df.groupby('Brand_format').agg({
        'Плановые продажи, шт': 'sum',
        'Факт продажи, шт.': 'sum',
        'Плановые продажи, руб': 'sum',
        'Факт продажи, руб (от ЦМ)': 'sum',
        'Плановые затраты «Листинг/безусловные выплаты», руб': 'sum',
        'Фактические затраты «Листинг/безусловные выплаты», руб': 'sum',
        'Плановые затраты «Скидка в цене», руб': 'sum',
        'Фактические затраты «Скидка в цене», руб': 'sum',
        'Плановые затраты «Ретро», руб': 'sum',
        'Фактические затраты «Ретро», руб': 'sum',
        'Плановые затраты «Маркетинг», руб': 'sum',
        'Фактические затраты «Маркетинг», руб': 'sum',
        'Плановые затраты «Промо-скидка», руб': 'sum',
        'Фактические затраты «Промо-скидка», руб': 'sum',
        'план затарты': 'sum',
        'факт затраты': 'sum',
        'доход план': 'sum',
        'доход факт': 'sum'
    }).reset_index()
    
    # Добавляем расчетные столбцы
    sku_data['Выполнение плана (руб), %'] = (
        sku_data['Факт продажи, руб (от ЦМ)'] / sku_data['Плановые продажи, руб'] * 100
    ).round(1)
    
    sku_data['Выполнение плана (шт), %'] = (
        sku_data['Факт продажи, шт.'] / sku_data['Плановые продажи, шт'] * 100
    ).round(1)
    
    # Форматируем числа
    for col in sku_data.columns:
        if 'руб' in col or 'затарты' in col or 'доход' in col:
            sku_data[col] = sku_data[col].apply(lambda x: f'{x:,.0f}' if pd.notna(x) else '0')
        elif 'шт' in col:
            sku_data[col] = sku_data[col].apply(lambda x: f'{x:,.0f}' if pd.notna(x) else '0')
    
    # Создаем таблицу
    table = dash_table.DataTable(
        data=sku_data.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in sku_data.columns],
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'fontSize': '12px',
            'fontFamily': 'Arial'
        },
        style_header={
            'backgroundColor': '#2c3e50',
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f8f9fa'
            },
            {
                'if': {
                    'column_id': 'Выполнение плана (руб), %',
                    'filter_query': '{Выполнение плана (руб), %} >= 100'
                },
                'backgroundColor': '#d4edda',
                'color': '#155724'
            },
            {
                'if': {
                    'column_id': 'Выполнение плана (руб), %',
                    'filter_query': '{Выполнение плана (руб), %} < 100'
                },
                'backgroundColor': '#f8d7da',
                'color': '#721c24'
            }
        ],
        page_size=20,
        sort_action='native',
        filter_action='native',
        export_format='xlsx',
        export_headers='display'
    )
    
    return table

def create_sku_chart(filtered_df):
    """График по SKU"""
    sku_data = filtered_df.groupby('Brand_format').agg({
        'Плановые продажи, руб': 'sum',
        'Факт продажи, руб (от ЦМ)': 'sum'
    }).reset_index()
    
    sku_data['Выполнение плана, %'] = (
        sku_data['Факт продажи, руб (от ЦМ)'] / sku_data['Плановые продажи, руб'] * 100
    )
    
    sku_data = sku_data.sort_values('Факт продажи, руб (от ЦМ)', ascending=True).tail(15)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=sku_data['Brand_format'],
        x=sku_data['Факт продажи, руб (от ЦМ)'],
        orientation='h',
        marker=dict(
            color=sku_data['Выполнение плана, %'],
            colorscale='RdYlGn',
            cmin=0,
            cmax=150,
            colorbar=dict(title="Выполнение<br>плана, %")
        ),
        text=sku_data['Выполнение плана, %'].apply(lambda x: f'{x:.0f}%'),
        textposition='auto',
        name='Факт продажи'
    ))
    
    fig.update_layout(
        title='ТОП-15 SKU по продажам (цвет = выполнение плана)',
        xaxis_title='Продажи, руб',
        yaxis_title='SKU (Brand_format)',
        height=600,
        template='plotly_white'
    )
    
    return fig

# Запуск приложения
if __name__ == '__main__':
    print("="*80)
    print("🚀 BI Dashboard (Расширенная версия) запускается...")
    print("="*80)
    print("\n📊 Откройте в браузере: http://localhost:8051")
    print("\n💡 Новые возможности:")
    print("   - Фильтр по контрактам")
    print("   - Информация о датах контракта")
    print("   - Детализация до SKU")
    print("   - Все плановые и фактические расходы")
    print("\n💡 Для остановки нажмите Ctrl+C")
    print("="*80)
    app.run(debug=False, host='0.0.0.0', port=8051)
