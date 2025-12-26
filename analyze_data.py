import pandas as pd
import numpy as np

# Читаем данные
df = pd.read_excel('/workspace/data.xlsx')

print('='*80)
print('СТРУКТУРА ДАННЫХ')
print('='*80)
print(f'\nРазмер данных: {df.shape[0]} строк x {df.shape[1]} столбцов')

print('\n' + '='*80)
print('СПИСОК СТОЛБЦОВ')
print('='*80)
for i, col in enumerate(df.columns, 1):
    print(f'{i}. {col}')

print('\n' + '='*80)
print('ТИПЫ ДАННЫХ')
print('='*80)
print(df.dtypes)

print('\n' + '='*80)
print('ПЕРВЫЕ 5 СТРОК')
print('='*80)
print(df.head(5))

print('\n' + '='*80)
print('СТАТИСТИКА ПО ЧИСЛОВЫМ СТОЛБЦАМ')
print('='*80)
print(df.describe())

print('\n' + '='*80)
print('ИНФОРМАЦИЯ О ПРОПУЩЕННЫХ ЗНАЧЕНИЯХ')
print('='*80)
missing = df.isnull().sum()
missing_pct = (df.isnull().sum() / len(df)) * 100
missing_df = pd.DataFrame({'Пропущено': missing, 'Процент': missing_pct})
print(missing_df[missing_df['Пропущено'] > 0])

print('\n' + '='*80)
print('УНИКАЛЬНЫЕ ЗНАЧЕНИЯ В КЛЮЧЕВЫХ СТОЛБЦАХ')
print('='*80)
for col in df.columns[:15]:
    unique_count = df[col].nunique()
    print(f'{col}: {unique_count} уникальных значений')
    if unique_count <= 10:
        print(f'   Значения: {df[col].unique()[:10].tolist()}')
