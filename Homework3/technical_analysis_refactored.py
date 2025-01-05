import pandas as pd
import numpy as np
from typing import Dict, Any


def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators for the given dataframe"""
    data = df.copy()

    # Use 'Avg Price' column for calculations
    price = data['Avg Price']

    # Calculate Moving Averages
    data['SMA_10'] = price.rolling(window=10).mean()
    data['EMA_20'] = price.ewm(span=20, adjust=False).mean()
    data['SMA_50'] = price.rolling(window=50).mean()

    # Weighted Moving Average
    weights = np.arange(1, 16)
    data['WMA_15'] = price.rolling(window=15).apply(
        lambda x: np.sum(weights[:len(x)] * x) / np.sum(weights[:len(x)])
    )

    # Hull Moving Average
    def hull_moving_average(series, window=9):
        half_length = int(window / 2)
        sqrt_length = int(np.sqrt(window))

        wmaf = series.rolling(window=half_length).apply(
            lambda x: np.sum(np.arange(1, len(x) + 1) * x) / np.sum(np.arange(1, len(x) + 1))
        )
        wmas = series.rolling(window=window).apply(
            lambda x: np.sum(np.arange(1, len(x) + 1) * x) / np.sum(np.arange(1, len(x) + 1))
        )

        hull = (2 * wmaf - wmas).rolling(window=sqrt_length).mean()
        return hull

    data['HMA_9'] = hull_moving_average(price, 9)

    # RSI
    delta = price.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))

    # Stochastic
    low_14 = data['Min'].rolling(window=14).min()
    high_14 = data['Max'].rolling(window=14).max()
    data['Stochastic'] = 100 * ((price - low_14) / (high_14 - low_14))

    # MACD
    exp1 = price.ewm(span=12, adjust=False).mean()
    exp2 = price.ewm(span=26, adjust=False).mean()
    data['MACD'] = exp1 - exp2

    # Williams %R
    high = data['Max'].rolling(window=14).max()
    low = data['Min'].rolling(window=14).min()
    data['Williams_R'] = ((high - price) / (high - low)) * -100

    return data


def generate_signal(row: pd.Series) -> str:
    """Generate trading signal based on technical indicators"""
    signals = []

    # RSI signals
    if pd.notna(row['RSI']):
        if row['RSI'] > 70:
            signals.append('sell')
        elif row['RSI'] < 30:
            signals.append('buy')
        else:
            signals.append('hold')

    # Stochastic signals
    if pd.notna(row['Stochastic']):
        if row['Stochastic'] > 80:
            signals.append('sell')
        elif row['Stochastic'] < 20:
            signals.append('buy')
        else:
            signals.append('hold')

    # MACD signals
    if pd.notna(row['MACD']):
        if row['MACD'] > 0:
            signals.append('buy')
        elif row['MACD'] < 0:
            signals.append('sell')
        else:
            signals.append('hold')

    # Williams %R signals
    if pd.notna(row['Williams_R']):
        if row['Williams_R'] > -20:
            signals.append('sell')
        elif row['Williams_R'] < -80:
            signals.append('buy')
        else:
            signals.append('hold')

    # Count signals
    if signals:
        buy_count = signals.count('buy')
        sell_count = signals.count('sell')
        hold_count = signals.count('hold')

        # Final decision
        if buy_count > sell_count and buy_count > hold_count:
            return 'buy'
        elif sell_count > buy_count and sell_count > hold_count:
            return 'sell'

    return 'hold'


def analyze_timeframe(df: pd.DataFrame, period_days: int) -> Dict[str, Any]:
    """Analyze a specific timeframe and return the results"""
    if len(df) < period_days:
        return None

    # Get the data for the specified period
    df_period = df.tail(period_days)

    # Calculate indicators
    df_with_indicators = calculate_technical_indicators(df_period)

    # Generate signal for the latest data point
    latest_data = df_with_indicators.iloc[-1]

    # Get the date from the Date column instead of the index
    latest_date = df_period['Date'].iloc[-1]
    date_str = latest_date.strftime('%Y-%m-%d') if isinstance(latest_date, pd.Timestamp) else str(latest_date)

    # Return the results as a dictionary with all requested indicators
    return {
        'Date': date_str,
        'Avg Price': round(latest_data['Avg Price'], 2),
        'SMA_10': round(latest_data['SMA_10'], 2) if pd.notna(latest_data['SMA_10']) else None,
        'EMA_20': round(latest_data['EMA_20'], 2) if pd.notna(latest_data['EMA_20']) else None,
        'WMA_15': round(latest_data['WMA_15'], 2) if pd.notna(latest_data['WMA_15']) else None,
        'HMA_9': round(latest_data['HMA_9'], 2) if pd.notna(latest_data['HMA_9']) else None,
        'RSI': round(latest_data['RSI'], 2) if pd.notna(latest_data['RSI']) else None,
        'Stochastic': round(latest_data['Stochastic'], 2) if pd.notna(latest_data['Stochastic']) else None,
        'MACD': round(latest_data['MACD'], 2) if pd.notna(latest_data['MACD']) else None,
        'Williams_R': round(latest_data['Williams_R'], 2) if pd.notna(latest_data['Williams_R']) else None,
        'Signal': generate_signal(latest_data)
    }


def perform_technical_analysis(df: pd.DataFrame, company: str) -> str:
    """Generate HTML output for technical analysis results"""
    # Define timeframes
    timeframes = {
        '1 day': 1,
        '1 week': 5,
        '1 month': 22
    }

    # Calculate analysis for each timeframe
    results = {}
    for period_name, days in timeframes.items():
        analysis = analyze_timeframe(df, days)
        if analysis:
            results[period_name] = analysis

    # Generate HTML table for each timeframe
    html_output = f"<h2>Technical Analysis Results for {company}</h2>"

    # Define the order of indicators to display
    display_order = [
        'Avg Price', 'SMA_10', 'EMA_20', 'WMA_15', 'HMA_9',
        'RSI', 'Stochastic', 'MACD', 'Williams_R', 'Signal'
    ]

    for period_name, analysis in results.items():
        if analysis:
            html_output += f"<h3>{period_name}</h3>"
            html_output += """
            <table class='table table-striped'>
                <thead>
                    <tr>
                        <th>Indicator</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
            """

            # Display indicators in the specified order
            for indicator in display_order:
                if indicator in analysis and analysis[indicator] is not None:
                    html_output += f"<tr><td>{indicator}</td><td>{analysis[indicator]}</td></tr>"

            html_output += "</tbody></table>"

    return html_output