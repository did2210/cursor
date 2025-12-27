#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BI Dashboard для анализа продаж и затрат
Интерактивная визуализация план/факт показателей
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from datetime import datetime
import numpy as np
import os

# Загрузка данных
def load_data(file_path=None):
    """Загружает и подготавливает данные из Excel"""
    # Определяем путь к файлу
    if file_path is None:
        # Проверяем переменную окружения
        file_path = os.environ.get('DATA_FILE_PATH', 'data.xlsx')
    
    print(f"📂 Загрузка данных из: {file_path}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    
    df = pd.read_excel(file_path)
    
    # Заполняем пропуски нулями для числовых столбцов
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
    
    # Рентабельность
    df['Рентабельность план, %'] = np.where(
        df['Плановые продажи, руб'] != 0,
        (df['доход план'] / df['Плановые продажи, руб'] * 100),
        0
    )
    
    df['Рентабельность факт, %'] = np.where(
        df['Факт продажи, руб (от ЦМ)'] != 0,
        (df['доход факт'] / df['Факт продажи, руб (от ЦМ)'] * 100),
        0
    )
    
    return df

# Инициализация приложения
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "BI Dashboard - Анализ продаж"

# Загружаем данные
df = load_data()

# Стили
CARD_STYLE = {
    'box-shadow': '0 4px 6px 0 rgba(0, 0, 0, 0.18)',
    'margin-bottom': '20px',
    'border-radius': '10px',
    'padding': '20px'
}

# Функции для создания графиков

def create_kpi_cards():
    """Создает карточки с основными KPI"""
    
    # Расчет метрик
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
    
    cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("💰 Продажи (руб)", className="card-title"),
                    html.H2(f"{total_fact_sales:,.0f}", style={'color': '#1f77b4'}),
                    html.P(f"План: {total_plan_sales:,.0f}"),
                    html.H5(f"{plan_execution:.1f}% выполнения", 
                           style={'color': 'green' if plan_execution >= 100 else 'red'})
                ])
            ], style=CARD_STYLE)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("📦 Продажи (шт)", className="card-title"),
                    html.H2(f"{total_fact_units:,.0f}", style={'color': '#ff7f0e'}),
                    html.P(f"План: {total_plan_units:,.0f}"),
                    html.H5(f"{units_execution:.1f}% выполнения",
                           style={'color': 'green' if units_execution >= 100 else 'red'})
                ])
            ], style=CARD_STYLE)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("💵 Доход", className="card-title"),
                    html.H2(f"{total_fact_income:,.0f}", style={'color': '#2ca02c'}),
                    html.P(f"План: {total_plan_income:,.0f}"),
                    html.H5(f"{income_execution:.1f}% выполнения",
                           style={'color': 'green' if income_execution >= 100 else 'red'})
                ])
            ], style=CARD_STYLE)
        ], width=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("💸 Затраты", className="card-title"),
                    html.H2(f"{total_fact_costs:,.0f}", style={'color': '#d62728'}),
                    html.P(f"План: {total_plan_costs:,.0f}"),
                    html.H5(f"{(total_fact_costs/total_plan_costs*100):.1f}% от плана" 
                           if total_plan_costs > 0 else "N/A",
                           style={'color': 'orange'})
                ])
            ], style=CARD_STYLE)
        ], width=3),
    ])
    
    return cards

def create_plan_fact_chart():
    """График план/факт продаж по месяцам"""
    monthly_data = df.groupby('Дата').agg({
        'Плановые продажи, руб': 'sum',
        'Факт продажи, руб (от ЦМ)': 'sum',
        'доход план': 'sum',
        'доход факт': 'sum'
    }).reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=monthly_data['Дата'],
        y=monthly_data['Плановые продажи, руб'],
        name='План продажи',
        marker_color='lightblue',
        opacity=0.7
    ))
    
    fig.add_trace(go.Bar(
        x=monthly_data['Дата'],
        y=monthly_data['Факт продажи, руб (от ЦМ)'],
        name='Факт продажи',
        marker_color='darkblue'
    ))
    
    fig.update_layout(
        title='План/Факт продаж по месяцам (руб)',
        xaxis_title='Месяц',
        yaxis_title='Продажи, руб',
        barmode='group',
        height=400,
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

def create_execution_trend():
    """График тренда выполнения плана"""
    monthly_data = df.groupby('Дата').agg({
        'Плановые продажи, руб': 'sum',
        'Факт продажи, руб (от ЦМ)': 'sum',
        'Плановые продажи, шт': 'sum',
        'Факт продажи, шт.': 'sum'
    }).reset_index()
    
    monthly_data['Выполнение плана (руб), %'] = (
        monthly_data['Факт продажи, руб (от ЦМ)'] / 
        monthly_data['Плановые продажи, руб'] * 100
    )
    
    monthly_data['Выполнение плана (шт), %'] = (
        monthly_data['Факт продажи, шт.'] / 
        monthly_data['Плановые продажи, шт'] * 100
    )
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=monthly_data['Дата'],
        y=monthly_data['Выполнение плана (руб), %'],
        mode='lines+markers',
        name='Выполнение плана (руб)',
        line=dict(color='blue', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=monthly_data['Дата'],
        y=monthly_data['Выполнение плана (шт), %'],
        mode='lines+markers',
        name='Выполнение плана (шт)',
        line=dict(color='green', width=3),
        marker=dict(size=8)
    ))
    
    # Линия 100%
    fig.add_hline(y=100, line_dash="dash", line_color="red", 
                  annotation_text="Цель 100%")
    
    fig.update_layout(
        title='Динамика выполнения плана продаж',
        xaxis_title='Месяц',
        yaxis_title='Выполнение плана, %',
        height=400,
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

def create_network_analysis():
    """Анализ по торговым сетям"""
    network_data = df.groupby('Сеть').agg({
        'Факт продажи, руб (от ЦМ)': 'sum',
        'доход факт': 'sum'
    }).reset_index()
    
    network_data = network_data.sort_values('Факт продажи, руб (от ЦМ)', ascending=False).head(15)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=network_data['Сеть'],
        x=network_data['Факт продажи, руб (от ЦМ)'],
        orientation='h',
        name='Продажи',
        marker_color='steelblue',
        text=network_data['Факт продажи, руб (от ЦМ)'].apply(lambda x: f'{x/1e6:.1f}M'),
        textposition='auto'
    ))
    
    fig.update_layout(
        title='ТОП-15 торговых сетей по продажам',
        xaxis_title='Продажи, руб',
        yaxis_title='Торговая сеть',
        height=500,
        template='plotly_white'
    )
    
    return fig

def create_product_analysis():
    """Анализ по продуктам"""
    product_data = df.groupby('Brand_format').agg({
        'Плановые продажи, руб': 'sum',
        'Факт продажи, руб (от ЦМ)': 'sum',
        'Плановые продажи, шт': 'sum',
        'Факт продажи, шт.': 'sum'
    }).reset_index()
    
    product_data['Выполнение плана, %'] = (
        product_data['Факт продажи, руб (от ЦМ)'] / 
        product_data['Плановые продажи, руб'] * 100
    )
    
    product_data = product_data.sort_values('Факт продажи, руб (от ЦМ)', ascending=True).tail(15)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=product_data['Brand_format'],
        x=product_data['Факт продажи, руб (от ЦМ)'],
        orientation='h',
        marker_color=product_data['Выполнение плана, %'],
        marker_colorscale='RdYlGn',
        marker_cmin=0,
        marker_cmax=150,
        text=product_data['Выполнение плана, %'].apply(lambda x: f'{x:.0f}%'),
        textposition='auto',
        name='Продажи'
    ))
    
    fig.update_layout(
        title='ТОП-15 продуктов по продажам (цвет = выполнение плана)',
        xaxis_title='Продажи, руб',
        yaxis_title='Продукт',
        height=500,
        template='plotly_white',
        coloraxis_colorbar=dict(title="Выполнение плана, %")
    )
    
    return fig

def create_costs_breakdown():
    """Разбивка затрат по типам"""
    costs_data = {
        'Тип затрат': [
            'Листинг/безусловные',
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
        title='План/Факт затрат по типам',
        xaxis_title='Тип затрат',
        yaxis_title='Сумма, руб',
        barmode='group',
        height=400,
        template='plotly_white'
    )
    
    return fig

def create_income_vs_costs():
    """График доходов vs затрат"""
    monthly_data = df.groupby('Дата').agg({
        'доход план': 'sum',
        'доход факт': 'sum',
        'план затарты': 'sum',
        'факт затраты': 'sum',
        'Факт продажи, руб (от ЦМ)': 'sum'
    }).reset_index()
    
    monthly_data['Рентабельность план, %'] = (
        monthly_data['доход план'] / monthly_data['Факт продажи, руб (от ЦМ)'] * 100
    )
    
    monthly_data['Рентабельность факт, %'] = (
        monthly_data['доход факт'] / monthly_data['Факт продажи, руб (от ЦМ)'] * 100
    )
    
    # Создаем subplot с двумя осями Y
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Bar(x=monthly_data['Дата'], y=monthly_data['доход факт'],
               name='Доход факт', marker_color='lightgreen'),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Bar(x=monthly_data['Дата'], y=monthly_data['факт затраты'],
               name='Затраты факт', marker_color='lightcoral'),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=monthly_data['Дата'], y=monthly_data['Рентабельность факт, %'],
                   name='Рентабельность, %', line=dict(color='blue', width=3),
                   mode='lines+markers'),
        secondary_y=True
    )
    
    fig.update_layout(
        title='Доходы, затраты и рентабельность по месяцам',
        height=400,
        hovermode='x unified',
        template='plotly_white'
    )
    
    fig.update_xaxis(title_text="Месяц")
    fig.update_yaxis(title_text="Сумма, руб", secondary_y=False)
    fig.update_yaxis(title_text="Рентабельность, %", secondary_y=True)
    
    return fig

def create_sales_group_analysis():
    """Анализ по группам сбыта"""
    group_data = df.groupby('группа сбыта2').agg({
        'Факт продажи, руб (от ЦМ)': 'sum',
        'доход факт': 'sum',
        'Плановые продажи, руб': 'sum'
    }).reset_index()
    
    group_data['Выполнение плана, %'] = (
        group_data['Факт продажи, руб (от ЦМ)'] / 
        group_data['Плановые продажи, руб'] * 100
    )
    
    fig = go.Figure(data=[
        go.Pie(
            labels=group_data['группа сбыта2'],
            values=group_data['Факт продажи, руб (от ЦМ)'],
            hole=0.4,
            marker_colors=px.colors.qualitative.Set3
        )
    ])
    
    fig.update_layout(
        title='Распределение продаж по группам сбыта',
        height=400,
        template='plotly_white'
    )
    
    return fig

# Layout приложения
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("📊 BI Dashboard - Анализ продаж и затрат", 
                   style={'textAlign': 'center', 'margin': '30px', 'color': '#2c3e50'}),
            html.Hr()
        ])
    ]),
    
    # KPI карточки
    html.Div(id='kpi-cards'),
    
    html.Br(),
    
    # Основные графики
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='plan-fact-chart')
        ], width=6),
        dbc.Col([
            dcc.Graph(id='execution-trend')
        ], width=6)
    ]),
    
    html.Br(),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='income-costs-chart')
        ], width=6),
        dbc.Col([
            dcc.Graph(id='costs-breakdown')
        ], width=6)
    ]),
    
    html.Br(),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='network-analysis')
        ], width=6),
        dbc.Col([
            dcc.Graph(id='product-analysis')
        ], width=6)
    ]),
    
    html.Br(),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='sales-group-analysis')
        ], width=12)
    ]),
    
    html.Br(),
    html.Hr(),
    
    html.Footer([
        html.P(f"Последнее обновление: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
               style={'textAlign': 'center', 'color': 'gray'})
    ])
    
], fluid=True, style={'backgroundColor': '#f8f9fa'})

# Callbacks для обновления графиков
@app.callback(
    Output('kpi-cards', 'children'),
    Input('kpi-cards', 'id')
)
def update_kpi_cards(_):
    return create_kpi_cards()

@app.callback(
    Output('plan-fact-chart', 'figure'),
    Input('plan-fact-chart', 'id')
)
def update_plan_fact(_):
    return create_plan_fact_chart()

@app.callback(
    Output('execution-trend', 'figure'),
    Input('execution-trend', 'id')
)
def update_execution(_):
    return create_execution_trend()

@app.callback(
    Output('network-analysis', 'figure'),
    Input('network-analysis', 'id')
)
def update_network(_):
    return create_network_analysis()

@app.callback(
    Output('product-analysis', 'figure'),
    Input('product-analysis', 'id')
)
def update_product(_):
    return create_product_analysis()

@app.callback(
    Output('costs-breakdown', 'figure'),
    Input('costs-breakdown', 'id')
)
def update_costs(_):
    return create_costs_breakdown()

@app.callback(
    Output('income-costs-chart', 'figure'),
    Input('income-costs-chart', 'id')
)
def update_income_costs(_):
    return create_income_vs_costs()

@app.callback(
    Output('sales-group-analysis', 'figure'),
    Input('sales-group-analysis', 'id')
)
def update_sales_group(_):
    return create_sales_group_analysis()

# Запуск приложения
if __name__ == '__main__':
    print("="*80)
    print("🚀 BI Dashboard запускается...")
    print("="*80)
    print("\n📊 Откройте в браузере: http://localhost:8050")
    print("\n💡 Для остановки нажмите Ctrl+C")
    print("="*80)
    app.run(debug=False, host='0.0.0.0', port=8050)
