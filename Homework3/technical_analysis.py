import ta
import pandas as pd
import numpy as np


def perform_technical_analysis(data, company):
    data = data.copy()

    numeric_columns = ['Max', 'Min', 'Last trade price', 'Avg Price']
    for col in numeric_columns:
        data[col] = data[col].astype(str).str.replace(',', '').str.replace('$', '')
        data[col] = pd.to_numeric(data[col], errors='coerce')

    data['High'] = data['Max']
    data['Low'] = data['Min']
    data['Close'] = data['Last trade price']

    time_periods = {'1 day': 1, '1 week': 5, '1 month': 22}
    indicators = {}

    for period, days in time_periods.items():
        period_data = data.tail(days).copy()

        if period_data['Avg Price'].isna().all():
            indicators[period] = f"<p>No valid data available for {period}</p>"
            continue

        try:
            period_data['SMA_10'] = period_data['Avg Price'].rolling(window=min(10, len(period_data))).mean()
            period_data['EMA_10'] = period_data['Avg Price'].ewm(span=min(10, len(period_data)), adjust=False).mean()

            rsi_indicator = ta.momentum.RSIIndicator(period_data['Avg Price'])
            period_data['RSI'] = rsi_indicator.rsi()

            valid_rows = period_data['RSI'].notna()

            period_data['Buy_Signal'] = False
            period_data['Sell_Signal'] = False
            period_data['Signal'] = 'hold'

            if valid_rows.any():
                rsi_values = period_data.loc[valid_rows, 'RSI']
                sma_values = period_data.loc[valid_rows, 'SMA_10']
                ema_values = period_data.loc[valid_rows, 'EMA_10']

                buy_condition = (rsi_values < 30) & (sma_values > ema_values)
                period_data.loc[buy_condition.index[buy_condition], 'Buy_Signal'] = True
                period_data.loc[buy_condition.index[buy_condition], 'Signal'] = 'buy'

                sell_condition = (rsi_values > 70) & (sma_values < ema_values)
                period_data.loc[sell_condition.index[sell_condition], 'Sell_Signal'] = True
                period_data.loc[sell_condition.index[sell_condition], 'Signal'] = 'sell'

            numeric_cols = ['Avg Price', 'SMA_10', 'EMA_10', 'RSI']
            for col in numeric_cols:
                period_data[col] = period_data[col].apply(
                    lambda x: f'{x:.2f}' if pd.notnull(x) else ''
                )

            display_cols = ['Date', 'Avg Price', 'SMA_10', 'EMA_10', 'RSI', 'Signal']
            indicators[period] = period_data[display_cols].to_html(
                index=False,
                classes='table table-striped'
            )

        except Exception as e:
            indicators[period] = f"<p>Error processing data for {period}: {str(e)}</p>"

    result_html = f"<h2>Technical Analysis for {company}</h2>"
    for period, table_html in indicators.items():
        result_html += f"<h3>{period}</h3>{table_html}"

    return result_html