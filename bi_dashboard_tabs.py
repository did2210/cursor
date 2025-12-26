#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BI Dashboard с вкладками по контрактам
Глубокая визуализация каждого контракта отдельно
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
    
    return df

# Инициализация приложения
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "BI Dashboard - Анализ по контрактам"

# Загружаем данные
df = load_data()

# Получаем список уникальных контрактов
contracts = sorted(df['Контракт'].unique())

print(f"\n✅ Загружено {len(df)} записей")
print(f"✅ Найдено {len(contracts)} контрактов")
print(f"\nСоздаем вкладки для контрактов...")

# Стили
CARD_STYLE = {
    'box-shadow': '0 4px 6px 0 rgba(0, 0, 0, 0.18)',
    'margin-bottom': '20px',
    'border-radius': '10px',
    'padding': '20px',
    'backgroundColor': 'white'
}

def create_contract_header(contract_name, contract_df):
    """Создает заголовок вкладки с информацией о контракте"""
    if contract_df.empty:
        return html.Div()
    
    # Информация о контракте
    first_row = contract_df.iloc[0]
    start_date = first_row['начало_контракта']
    end_date = first_row['конец_контракта']
    network = first_row['Сеть']
    status = first_row['контракт2']
    group = first_row['группа сбыта']
    
    # Период данных
    min_date = contract_df['Дата'].min()
    max_date = contract_df['Дата'].max()
    
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H3([
                        html.I(className="fas fa-file-contract", style={'marginRight': '10px'}),
                        contract_name
                    ], style={'color': '#2c3e50', 'marginBottom': '20px'}),
                ], width=12)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("🏪 Торговая сеть", style={'color': '#7f8c8d', 'marginBottom': '5px'}),
                            html.H4(network, style={'color': '#2c3e50', 'marginBottom': '0'})
                        ])
                    ], style={'padding': '15px', 'backgroundColor': '#ecf0f1'})
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("📅 Начало контракта", style={'color': '#7f8c8d', 'marginBottom': '5px'}),
                            html.H4(start_date.strftime('%d.%m.%Y') if pd.notna(start_date) else 'Н/Д',
                                   style={'color': '#27ae60', 'marginBottom': '0'})
                        ])
                    ], style={'padding': '15px', 'backgroundColor': '#d5f4e6'})
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("📅 Конец контракта", style={'color': '#7f8c8d', 'marginBottom': '5px'}),
                            html.H4(end_date.strftime('%d.%m.%Y') if pd.notna(end_date) else 'Н/Д',
                                   style={'color': '#e74c3c', 'marginBottom': '0'})
                        ])
                    ], style={'padding': '15px', 'backgroundColor': '#fadbd8'})
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("📊 Статус контракта", style={'color': '#7f8c8d', 'marginBottom': '5px'}),
                            html.H4([
                                html.Span(status, style={
                                    'backgroundColor': '#28a745' if status == 'действующий' else '#dc3545',
                                    'color': 'white',
                                    'padding': '8px 15px',
                                    'borderRadius': '5px',
                                    'fontSize': '18px'
                                })
                            ], style={'marginBottom': '0'})
                        ])
                    ], style={'padding': '15px', 'backgroundColor': '#fff3cd'})
                ], width=3),
            ]),
            html.Hr(style={'margin': '20px 0'}),
            dbc.Row([
                dbc.Col([
                    html.P([
                        html.Strong("Группа сбыта: "), 
                        html.Span(group, style={'color': '#3498db', 'fontSize': '16px'})
                    ], style={'marginBottom': '5px'}),
                    html.P([
                        html.Strong("Период данных: "), 
                        html.Span(f"{min_date.strftime('%m.%Y')} - {max_date.strftime('%m.%Y')}", 
                                 style={'color': '#95a5a6', 'fontSize': '16px'})
                    ], style={'marginBottom': '5px'}),
                ], width=12)
            ])
        ])
    ], style=CARD_STYLE)

def create_kpi_section(contract_df):
    """Создает секцию KPI для контракта"""
    # Расчет метрик
    total_plan_sales_rub = contract_df['Плановые продажи, руб'].sum()
    total_fact_sales_rub = contract_df['Факт продажи, руб (от ЦМ)'].sum()
    total_plan_sales_units = contract_df['Плановые продажи, шт'].sum()
    total_fact_sales_units = contract_df['Факт продажи, шт.'].sum()
    
    plan_execution_rub = (total_fact_sales_rub / total_plan_sales_rub * 100) if total_plan_sales_rub > 0 else 0
    plan_execution_units = (total_fact_sales_units / total_plan_sales_units * 100) if total_plan_sales_units > 0 else 0
    
    total_plan_income = contract_df['доход план'].sum()
    total_fact_income = contract_df['доход факт'].sum()
    income_execution = (total_fact_income / total_plan_income * 100) if total_plan_income > 0 else 0
    
    total_plan_costs = contract_df['план затарты'].sum()
    total_fact_costs = contract_df['факт затраты'].sum()
    costs_execution = (total_fact_costs / total_plan_costs * 100) if total_plan_costs > 0 else 0
    
    # Рентабельность
    profitability_plan = (total_plan_income / total_plan_sales_rub * 100) if total_plan_sales_rub > 0 else 0
    profitability_fact = (total_fact_income / total_fact_sales_rub * 100) if total_fact_sales_rub > 0 else 0
    
    return html.Div([
        html.H4("📊 Ключевые показатели контракта", style={'marginBottom': '20px', 'color': '#2c3e50'}),
        
        # Основные KPI
        dbc.Row([
            # Продажи в рублях
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("💰 Продажи (руб)", style={'color': '#7f8c8d'}),
                        html.H2(f"{total_fact_sales_rub:,.0f} ₽", style={'color': '#3498db', 'marginBottom': '10px'}),
                        html.Hr(style={'margin': '10px 0'}),
                        html.P([
                            html.Strong("План: "),
                            f"{total_plan_sales_rub:,.0f} ₽"
                        ], style={'fontSize': '14px', 'marginBottom': '5px'}),
                        html.P([
                            html.Strong("Разница: "),
                            html.Span(f"{total_fact_sales_rub - total_plan_sales_rub:+,.0f} ₽",
                                     style={'color': 'green' if total_fact_sales_rub >= total_plan_sales_rub else 'red'})
                        ], style={'fontSize': '14px', 'marginBottom': '10px'}),
                        html.H4(f"{plan_execution_rub:.1f}%", 
                               style={'color': 'green' if plan_execution_rub >= 100 else 'red',
                                     'marginBottom': '5px'}),
                        dbc.Progress(value=min(plan_execution_rub, 100), 
                                    color='success' if plan_execution_rub >= 100 else 'danger',
                                    style={'height': '10px'})
                    ])
                ], style=CARD_STYLE)
            ], width=3),
            
            # Продажи в штуках
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("📦 Продажи (шт)", style={'color': '#7f8c8d'}),
                        html.H2(f"{total_fact_sales_units:,.0f}", style={'color': '#e67e22', 'marginBottom': '10px'}),
                        html.Hr(style={'margin': '10px 0'}),
                        html.P([
                            html.Strong("План: "),
                            f"{total_plan_sales_units:,.0f} шт"
                        ], style={'fontSize': '14px', 'marginBottom': '5px'}),
                        html.P([
                            html.Strong("Разница: "),
                            html.Span(f"{total_fact_sales_units - total_plan_sales_units:+,.0f} шт",
                                     style={'color': 'green' if total_fact_sales_units >= total_plan_sales_units else 'red'})
                        ], style={'fontSize': '14px', 'marginBottom': '10px'}),
                        html.H4(f"{plan_execution_units:.1f}%", 
                               style={'color': 'green' if plan_execution_units >= 100 else 'red',
                                     'marginBottom': '5px'}),
                        dbc.Progress(value=min(plan_execution_units, 100), 
                                    color='success' if plan_execution_units >= 100 else 'danger',
                                    style={'height': '10px'})
                    ])
                ], style=CARD_STYLE)
            ], width=3),
            
            # Доход
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("💵 Доход", style={'color': '#7f8c8d'}),
                        html.H2(f"{total_fact_income:,.0f} ₽", style={'color': '#27ae60', 'marginBottom': '10px'}),
                        html.Hr(style={'margin': '10px 0'}),
                        html.P([
                            html.Strong("План: "),
                            f"{total_plan_income:,.0f} ₽"
                        ], style={'fontSize': '14px', 'marginBottom': '5px'}),
                        html.P([
                            html.Strong("Разница: "),
                            html.Span(f"{total_fact_income - total_plan_income:+,.0f} ₽",
                                     style={'color': 'green' if total_fact_income >= total_plan_income else 'red'})
                        ], style={'fontSize': '14px', 'marginBottom': '10px'}),
                        html.H4(f"{income_execution:.1f}%", 
                               style={'color': 'green' if income_execution >= 100 else 'red',
                                     'marginBottom': '5px'}),
                        dbc.Progress(value=min(income_execution, 100), 
                                    color='success' if income_execution >= 100 else 'danger',
                                    style={'height': '10px'})
                    ])
                ], style=CARD_STYLE)
            ], width=3),
            
            # Затраты
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("💸 Затраты", style={'color': '#7f8c8d'}),
                        html.H2(f"{total_fact_costs:,.0f} ₽", style={'color': '#e74c3c', 'marginBottom': '10px'}),
                        html.Hr(style={'margin': '10px 0'}),
                        html.P([
                            html.Strong("План: "),
                            f"{total_plan_costs:,.0f} ₽"
                        ], style={'fontSize': '14px', 'marginBottom': '5px'}),
                        html.P([
                            html.Strong("Разница: "),
                            html.Span(f"{total_fact_costs - total_plan_costs:+,.0f} ₽",
                                     style={'color': 'red' if total_fact_costs > total_plan_costs else 'green'})
                        ], style={'fontSize': '14px', 'marginBottom': '10px'}),
                        html.H4(f"{costs_execution:.1f}%", 
                               style={'color': 'red' if costs_execution > 100 else 'green',
                                     'marginBottom': '5px'}),
                        dbc.Progress(value=min(costs_execution, 100), 
                                    color='danger' if costs_execution > 100 else 'success',
                                    style={'height': '10px'})
                    ])
                ], style=CARD_STYLE)
            ], width=3),
        ]),
        
        html.Br(),
        
        # Дополнительные метрики
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("📈 Рентабельность (план)", style={'color': '#7f8c8d', 'fontSize': '14px'}),
                        html.H3(f"{profitability_plan:.1f}%", style={'color': '#9b59b6', 'marginBottom': '0'})
                    ])
                ], style={'padding': '15px', 'backgroundColor': '#f4ecf7'})
            ], width=2),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("📈 Рентабельность (факт)", style={'color': '#7f8c8d', 'fontSize': '14px'}),
                        html.H3(f"{profitability_fact:.1f}%", style={'color': '#8e44ad', 'marginBottom': '0'})
                    ])
                ], style={'padding': '15px', 'backgroundColor': '#ebdef0'})
            ], width=2),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("📊 Средний чек (план)", style={'color': '#7f8c8d', 'fontSize': '14px'}),
                        html.H3(f"{total_plan_sales_rub/total_plan_sales_units:.2f} ₽" 
                               if total_plan_sales_units > 0 else "N/A",
                               style={'color': '#16a085', 'marginBottom': '0'})
                    ])
                ], style={'padding': '15px', 'backgroundColor': '#d1f2eb'})
            ], width=2),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("📊 Средний чек (факт)", style={'color': '#7f8c8d', 'fontSize': '14px'}),
                        html.H3(f"{total_fact_sales_rub/total_fact_sales_units:.2f} ₽" 
                               if total_fact_sales_units > 0 else "N/A",
                               style={'color': '#138d75', 'marginBottom': '0'})
                    ])
                ], style={'padding': '15px', 'backgroundColor': '#a9dfbf'})
            ], width=2),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("🎯 SKU в контракте", style={'color': '#7f8c8d', 'fontSize': '14px'}),
                        html.H3(f"{contract_df['Brand_format'].nunique()}", 
                               style={'color': '#d35400', 'marginBottom': '0'})
                    ])
                ], style={'padding': '15px', 'backgroundColor': '#fdebd0'})
            ], width=2),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("📅 Периодов данных", style={'color': '#7f8c8d', 'fontSize': '14px'}),
                        html.H3(f"{contract_df['Дата'].nunique()}", 
                               style={'color': '#c0392b', 'marginBottom': '0'})
                    ])
                ], style={'padding': '15px', 'backgroundColor': '#fadbd8'})
            ], width=2),
        ])
    ])

def create_costs_breakdown(contract_df):
    """Детальная разбивка затрат"""
    costs_data = {
        'Тип затрат': [
            'Листинг/безусловные',
            'Скидка в цене',
            'Ретро',
            'Маркетинг',
            'Промо-скидка',
            'Фонды'
        ],
        'План': [
            contract_df['Плановые затраты «Листинг/безусловные выплаты», руб'].sum(),
            contract_df['Плановые затраты «Скидка в цене», руб'].sum(),
            contract_df['Плановые затраты «Ретро», руб'].sum(),
            contract_df['Плановые затраты «Маркетинг», руб'].sum(),
            contract_df['Плановые затраты «Промо-скидка», руб'].sum(),
            contract_df['фонды'].sum()
        ],
        'Факт': [
            contract_df['Фактические затраты «Листинг/безусловные выплаты», руб'].sum(),
            contract_df['Фактические затраты «Скидка в цене», руб'].sum(),
            contract_df['Фактические затраты «Ретро», руб'].sum(),
            contract_df['Фактические затраты «Маркетинг», руб'].sum(),
            contract_df['Фактические затраты «Промо-скидка», руб'].sum(),
            contract_df['фонды'].sum()
        ]
    }
    
    costs_df = pd.DataFrame(costs_data)
    costs_df['Разница'] = costs_df['Факт'] - costs_df['План']
    costs_df['% от плана'] = (costs_df['Факт'] / costs_df['План'] * 100).fillna(0)
    
    return html.Div([
        html.H4("💸 Детальная разбивка затрат", style={'marginBottom': '20px', 'color': '#2c3e50'}),
        
        # Карточки по типам затрат
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6(row['Тип затрат'], style={'color': '#7f8c8d', 'fontSize': '13px', 'marginBottom': '10px'}),
                        html.H4(f"{row['Факт']:,.0f} ₽", style={'color': '#e74c3c', 'marginBottom': '5px'}),
                        html.P(f"План: {row['План']:,.0f} ₽", style={'fontSize': '12px', 'marginBottom': '5px'}),
                        html.P([
                            html.Strong(f"{row['% от плана']:.1f}%"),
                            html.Span(" от плана")
                        ], style={'fontSize': '12px', 'color': 'red' if row['% от плана'] > 100 else 'green'})
                    ])
                ], style={'padding': '15px', 'marginBottom': '15px', 'backgroundColor': '#fff5f5'})
            ], width=2) for idx, row in costs_df.iterrows()
        ])
    ])

def create_plan_fact_monthly_chart(contract_df):
    """График план/факт по месяцам"""
    monthly_data = contract_df.groupby('Дата').agg({
        'Плановые продажи, руб': 'sum',
        'Факт продажи, руб (от ЦМ)': 'sum',
        'Плановые продажи, шт': 'sum',
        'Факт продажи, шт.': 'sum'
    }).reset_index()
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Продажи в рублях', 'Продажи в штуках'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Продажи в рублях
    fig.add_trace(
        go.Bar(x=monthly_data['Дата'], y=monthly_data['Плановые продажи, руб'],
               name='План (руб)', marker_color='lightblue', opacity=0.6),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=monthly_data['Дата'], y=monthly_data['Факт продажи, руб (от ЦМ)'],
               name='Факт (руб)', marker_color='darkblue'),
        row=1, col=1
    )
    
    # Продажи в штуках
    fig.add_trace(
        go.Bar(x=monthly_data['Дата'], y=monthly_data['Плановые продажи, шт'],
               name='План (шт)', marker_color='lightcoral', opacity=0.6, showlegend=False),
        row=1, col=2
    )
    fig.add_trace(
        go.Bar(x=monthly_data['Дата'], y=monthly_data['Факт продажи, шт.'],
               name='Факт (шт)', marker_color='darkred', showlegend=False),
        row=1, col=2
    )
    
    fig.update_xaxes(title_text="Месяц", row=1, col=1)
    fig.update_xaxes(title_text="Месяц", row=1, col=2)
    fig.update_yaxes(title_text="Сумма, руб", row=1, col=1)
    fig.update_yaxes(title_text="Количество, шт", row=1, col=2)
    
    fig.update_layout(
        title_text="📊 План/Факт продаж по месяцам",
        height=400,
        hovermode='x unified',
        template='plotly_white',
        barmode='group'
    )
    
    return dcc.Graph(figure=fig)

def create_costs_chart(contract_df):
    """График затрат по типам"""
    costs_data = {
        'Тип': ['Листинг', 'Скидка', 'Ретро', 'Маркетинг', 'Промо', 'Фонды'],
        'План': [
            contract_df['Плановые затраты «Листинг/безусловные выплаты», руб'].sum(),
            contract_df['Плановые затраты «Скидка в цене», руб'].sum(),
            contract_df['Плановые затраты «Ретро», руб'].sum(),
            contract_df['Плановые затраты «Маркетинг», руб'].sum(),
            contract_df['Плановые затраты «Промо-скидка», руб'].sum(),
            contract_df['фонды'].sum()
        ],
        'Факт': [
            contract_df['Фактические затраты «Листинг/безусловные выплаты», руб'].sum(),
            contract_df['Фактические затраты «Скидка в цене», руб'].sum(),
            contract_df['Фактические затраты «Ретро», руб'].sum(),
            contract_df['Фактические затраты «Маркетинг», руб'].sum(),
            contract_df['Фактические затраты «Промо-скидка», руб'].sum(),
            contract_df['фонды'].sum()
        ]
    }
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=costs_data['Тип'], y=costs_data['План'],
                         name='План', marker_color='lightcoral'))
    fig.add_trace(go.Bar(x=costs_data['Тип'], y=costs_data['Факт'],
                         name='Факт', marker_color='darkred'))
    
    fig.update_layout(
        title='💸 Затраты по типам',
        xaxis_title='Тип затрат',
        yaxis_title='Сумма, руб',
        barmode='group',
        height=400,
        template='plotly_white'
    )
    
    return dcc.Graph(figure=fig)

def create_sku_table(contract_df):
    """Детальная таблица по Brand_format (SKU)"""
    sku_data = contract_df.groupby('Brand_format').agg({
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
    ).fillna(0).round(1)
    
    sku_data['Выполнение плана (шт), %'] = (
        sku_data['Факт продажи, шт.'] / sku_data['Плановые продажи, шт'] * 100
    ).fillna(0).round(1)
    
    sku_data['Рентабельность (факт), %'] = (
        sku_data['доход факт'] / sku_data['Факт продажи, руб (от ЦМ)'] * 100
    ).fillna(0).round(1)
    
    # Форматируем для отображения
    display_data = sku_data.copy()
    for col in display_data.columns:
        if 'руб' in col or 'затарты' in col or 'доход' in col:
            display_data[col] = display_data[col].apply(lambda x: f'{x:,.0f}')
        elif 'шт' in col:
            display_data[col] = display_data[col].apply(lambda x: f'{x:,.0f}')
    
    # Переименовываем столбцы для краткости
    display_data = display_data.rename(columns={
        'Brand_format': 'SKU',
        'Плановые продажи, шт': 'План шт',
        'Факт продажи, шт.': 'Факт шт',
        'Плановые продажи, руб': 'План руб',
        'Факт продажи, руб (от ЦМ)': 'Факт руб',
        'Плановые затраты «Листинг/безусловные выплаты», руб': 'План Листинг',
        'Фактические затраты «Листинг/безусловные выплаты», руб': 'Факт Листинг',
        'Плановые затраты «Скидка в цене», руб': 'План Скидка',
        'Фактические затраты «Скидка в цене», руб': 'Факт Скидка',
        'Плановые затраты «Ретро», руб': 'План Ретро',
        'Фактические затраты «Ретро», руб': 'Факт Ретро',
        'Плановые затраты «Маркетинг», руб': 'План Маркетинг',
        'Фактические затраты «Маркетинг», руб': 'Факт Маркетинг',
        'Плановые затраты «Промо-скидка», руб': 'План Промо',
        'Фактические затраты «Промо-скидка», руб': 'Факт Промо',
        'план затарты': 'План Затраты',
        'факт затраты': 'Факт Затраты',
        'доход план': 'План Доход',
        'доход факт': 'Факт Доход'
    })
    
    return html.Div([
        html.H4(f"🥤 Детальная разбивка по Brand_format (SKU) - всего {len(sku_data)} позиций", 
               style={'marginBottom': '20px', 'color': '#2c3e50'}),
        dash_table.DataTable(
            data=display_data.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in display_data.columns],
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '12px',
                'fontSize': '13px',
                'fontFamily': 'Arial',
                'minWidth': '100px'
            },
            style_header={
                'backgroundColor': '#34495e',
                'color': 'white',
                'fontWeight': 'bold',
                'textAlign': 'center',
                'padding': '12px'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#ecf0f1'
                },
                {
                    'if': {
                        'column_id': 'Выполнение плана (руб), %',
                    },
                    'backgroundColor': '#d4edda',
                    'color': '#155724',
                    'fontWeight': 'bold'
                },
                {
                    'if': {
                        'column_id': 'Рентабельность (факт), %',
                    },
                    'backgroundColor': '#fff3cd',
                    'color': '#856404',
                    'fontWeight': 'bold'
                }
            ],
            page_size=15,
            sort_action='native',
            filter_action='native',
            export_format='xlsx',
            export_headers='display',
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
            }
        )
    ])

def create_sku_chart(contract_df):
    """График по SKU"""
    sku_data = contract_df.groupby('Brand_format').agg({
        'Плановые продажи, руб': 'sum',
        'Факт продажи, руб (от ЦМ)': 'sum'
    }).reset_index()
    
    sku_data['Выполнение плана, %'] = (
        sku_data['Факт продажи, руб (от ЦМ)'] / sku_data['Плановые продажи, руб'] * 100
    ).fillna(0)
    
    sku_data = sku_data.sort_values('Факт продажи, руб (от ЦМ)', ascending=True)
    
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
        hovertemplate='<b>%{y}</b><br>Факт: %{x:,.0f} ₽<br>План: %{text}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'🥤 Продажи по Brand_format (всего {len(sku_data)} SKU)',
        xaxis_title='Продажи, руб',
        yaxis_title='Brand_format (SKU)',
        height=max(400, len(sku_data) * 25),
        template='plotly_white'
    )
    
    return dcc.Graph(figure=fig)

def create_contract_tab(contract_name, contract_df):
    """Создает содержимое вкладки для контракта"""
    return dbc.Container([
        html.Br(),
        
        # Заголовок с информацией о контракте
        create_contract_header(contract_name, contract_df),
        
        html.Br(),
        
        # KPI секция
        create_kpi_section(contract_df),
        
        html.Br(),
        
        # Детальная разбивка затрат
        create_costs_breakdown(contract_df),
        
        html.Br(),
        
        # Графики
        dbc.Row([
            dbc.Col([
                create_plan_fact_monthly_chart(contract_df)
            ], width=12)
        ]),
        
        html.Br(),
        
        dbc.Row([
            dbc.Col([
                create_costs_chart(contract_df)
            ], width=12)
        ]),
        
        html.Br(),
        
        # Таблица по SKU
        create_sku_table(contract_df),
        
        html.Br(),
        
        # График по SKU
        create_sku_chart(contract_df),
        
        html.Br(),
        
    ], fluid=True, style={'backgroundColor': '#f8f9fa', 'padding': '20px'})

# Создаем вкладки для каждого контракта
tabs = []
for contract in contracts:
    contract_df = df[df['Контракт'] == contract]
    tab = dbc.Tab(
        label=contract,
        tab_id=contract,
        children=create_contract_tab(contract, contract_df),
        style={'padding': '10px'},
        label_style={'fontSize': '12px', 'padding': '10px 15px'}
    )
    tabs.append(tab)
    print(f"  ✅ Создана вкладка: {contract}")

print(f"\n✅ Все вкладки готовы!")

# Layout приложения
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1([
                    html.I(className="fas fa-chart-line", style={'marginRight': '15px'}),
                    "BI Dashboard - Детальный анализ по контрактам"
                ], style={
                    'textAlign': 'center', 
                    'margin': '30px 0 20px 0', 
                    'color': 'white',
                    'textShadow': '2px 2px 4px rgba(0,0,0,0.3)'
                }),
                html.P(f"Всего контрактов: {len(contracts)} | Данные обновлены: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
                      style={'textAlign': 'center', 'color': 'white', 'fontSize': '16px'})
            ], style={
                'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'padding': '30px',
                'borderRadius': '10px',
                'marginBottom': '30px',
                'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
            })
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📑 Выберите контракт для детального анализа:", 
                           style={'marginBottom': '15px', 'color': '#2c3e50'}),
                    html.P("Каждая вкладка содержит полную информацию по контракту: даты, KPI, затраты, Brand_format (SKU) и графики",
                          style={'color': '#7f8c8d', 'fontSize': '14px'}),
                    dbc.Tabs(
                        tabs,
                        id="contract-tabs",
                        active_tab=contracts[0],
                        style={'marginTop': '10px'}
                    )
                ])
            ], style=CARD_STYLE)
        ], width=12)
    ]),
    
    html.Br(),
    html.Hr(),
    
    html.Footer([
        dbc.Row([
            dbc.Col([
                html.P([
                    html.I(className="fas fa-info-circle", style={'marginRight': '10px'}),
                    "Используйте вкладки для переключения между контрактами. ",
                    "Все данные обновляются автоматически."
                ], style={'textAlign': 'center', 'color': '#95a5a6', 'fontSize': '14px'})
            ])
        ])
    ], style={'marginTop': '30px', 'marginBottom': '20px'})
    
], fluid=True, style={'backgroundColor': '#ecf0f1', 'minHeight': '100vh'})

# Запуск приложения
if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 BI Dashboard с вкладками по контрактам запускается...")
    print("="*80)
    print("\n📊 Откройте в браузере: http://localhost:8052")
    print("\n✨ Особенности:")
    print("   ✅ Отдельная вкладка для каждого контракта")
    print("   ✅ Никаких общих данных - только детальный анализ")
    print("   ✅ Даты начала и конца контракта")
    print("   ✅ Все Brand_format (SKU) по контракту")
    print("   ✅ Все плановые и фактические расходы")
    print("   ✅ Интерактивные таблицы с экспортом в Excel")
    print("\n💡 Для остановки нажмите Ctrl+C")
    print("="*80 + "\n")
    app.run(debug=False, host='0.0.0.0', port=8052)
