from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Any


class TechnicalIndicator(ABC):
    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        pass

    @abstractmethod
    def generate_signal(self, value: float) -> str:
        pass


class RSIIndicator(TechnicalIndicator):
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        price = data['Avg Price']
        delta = price.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def generate_signal(self, value: float) -> str:
        if pd.isna(value):
            return 'hold'
        if value > 70:
            return 'sell'
        if value < 30:
            return 'buy'
        return 'hold'


class StochasticIndicator(TechnicalIndicator):
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        price = data['Avg Price']
        low_14 = data['Min'].rolling(window=14).min()
        high_14 = data['Max'].rolling(window=14).max()
        return 100 * ((price - low_14) / (high_14 - low_14))

    def generate_signal(self, value: float) -> str:
        if pd.isna(value):
            return 'hold'
        if value > 80:
            return 'sell'
        if value < 20:
            return 'buy'
        return 'hold'


class MACDIndicator(TechnicalIndicator):
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        price = data['Avg Price']
        exp1 = price.ewm(span=12, adjust=False).mean()
        exp2 = price.ewm(span=26, adjust=False).mean()
        return exp1 - exp2

    def generate_signal(self, value: float) -> str:
        if pd.isna(value):
            return 'hold'
        if value > 0:
            return 'buy'
        if value < 0:
            return 'sell'
        return 'hold'


class WilliamsRIndicator(TechnicalIndicator):
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        price = data['Avg Price']
        high = data['Max'].rolling(window=14).max()
        low = data['Min'].rolling(window=14).min()
        return ((high - price) / (high - low)) * -100

    def generate_signal(self, value: float) -> str:
        if pd.isna(value):
            return 'hold'
        if value > -20:
            return 'sell'
        if value < -80:
            return 'buy'
        return 'hold'


class MovingAverageFactory:
    @staticmethod
    def create_sma(price: pd.Series, window: int = 10) -> pd.Series:
        return price.rolling(window=window).mean()

    @staticmethod
    def create_ema(price: pd.Series, span: int = 20) -> pd.Series:
        return price.ewm(span=span, adjust=False).mean()

    @staticmethod
    def create_wma(price: pd.Series, window: int = 15) -> pd.Series:
        weights = np.arange(1, window + 1)
        return price.rolling(window=window).apply(
            lambda x: np.sum(weights[:len(x)] * x) / np.sum(weights[:len(x)])
        )

    @staticmethod
    def create_hma(price: pd.Series, window: int = 9) -> pd.Series:
        half_length = int(window / 2)
        sqrt_length = int(np.sqrt(window))

        weights = np.arange(1, half_length + 1)
        wmaf = price.rolling(window=half_length).apply(
            lambda x: np.sum(weights[:len(x)] * x) / np.sum(weights[:len(x)])
        )

        weights = np.arange(1, window + 1)
        wmas = price.rolling(window=window).apply(
            lambda x: np.sum(weights[:len(x)] * x) / np.sum(weights[:len(x)])
        )

        return (2 * wmaf - wmas).rolling(window=sqrt_length).mean()


class TechnicalAnalyzer:
    def __init__(self):
        self.indicators = {
            'RSI': RSIIndicator(),
            'Stochastic': StochasticIndicator(),
            'MACD': MACDIndicator(),
            'Williams_R': WilliamsRIndicator()
        }
        self.ma_factory = MovingAverageFactory()

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()
        price = data['Avg Price']

        # Calculate moving averages
        data['SMA'] = self.ma_factory.create_sma(price)
        data['EMA'] = self.ma_factory.create_ema(price)
        data['WMA'] = self.ma_factory.create_wma(price)
        data['HMA'] = self.ma_factory.create_hma(price)

        # Calculate technical indicators using strategy pattern
        for name, indicator in self.indicators.items():
            data[name] = indicator.calculate(data)

        return data

    def generate_signal(self, row: pd.Series) -> str:
        signals = []
        for name, indicator in self.indicators.items():
            if name in row:
                signals.append(indicator.generate_signal(row[name]))

        if signals:
            buy_count = signals.count('buy')
            sell_count = signals.count('sell')
            hold_count = signals.count('hold')

            if buy_count > sell_count and buy_count > hold_count:
                return 'buy'
            elif sell_count > buy_count and sell_count > hold_count:
                return 'sell'
        return 'hold'

    def analyze_timeframe(self, df: pd.DataFrame, period_days: int) -> Dict[str, Any]:
        if len(df) < period_days:
            return None

        df_period = df.tail(period_days)
        df_with_indicators = self.calculate_technical_indicators(df_period)
        latest_data = df_with_indicators.iloc[-1]
        latest_date = df_period['Date'].iloc[-1]
        date_str = latest_date.strftime('%Y-%m-%d') if isinstance(latest_date, pd.Timestamp) else str(latest_date)

        return {
            'Date': date_str,
            'Avg Price': round(latest_data['Avg Price'], 2),
            'SMA': round(latest_data['SMA'], 2) if pd.notna(latest_data['SMA']) else None,
            'EMA': round(latest_data['EMA'], 2) if pd.notna(latest_data['EMA']) else None,
            'WMA': round(latest_data['WMA'], 2) if pd.notna(latest_data['WMA']) else None,
            'HMA': round(latest_data['HMA'], 2) if pd.notna(latest_data['HMA']) else None,
            'RSI': round(latest_data['RSI'], 2) if pd.notna(latest_data['RSI']) else None,
            'Stochastic': round(latest_data['Stochastic'], 2) if pd.notna(latest_data['Stochastic']) else None,
            'MACD': round(latest_data['MACD'], 2) if pd.notna(latest_data['MACD']) else None,
            'Williams_R': round(latest_data['Williams_R'], 2) if pd.notna(latest_data['Williams_R']) else None,
            'Signal': self.generate_signal(latest_data)
        }


def perform_technical_analysis(df: pd.DataFrame, company: str) -> str:
    analyzer = TechnicalAnalyzer()
    timeframes = {
        '1 day': 1,
        '1 week': 5,
        '1 month': 22
    }

    results = {}
    for period_name, days in timeframes.items():
        analysis = analyzer.analyze_timeframe(df, days)
        if analysis:
            results[period_name] = analysis

    return generate_html_output(results, company)


def generate_html_output(results: Dict[str, Any], company: str) -> str:
    html_output = f"<h2>Technical Analysis Results for {company}</h2>"
    display_order = [
        'Avg Price', 'SMA', 'EMA', 'WMA', 'HMA',
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

            for indicator in display_order:
                if indicator in analysis and analysis[indicator] is not None:
                    html_output += f"<tr><td>{indicator}</td><td>{analysis[indicator]}</td></tr>"

            html_output += "</tbody></table>"

    return html_output


