import pandas as pd
import numpy as np


class TechnicalAnalyzer:
    def analyze(self, data: pd.DataFrame) -> dict:
        results = {}

        # Calculate RSI
        results['rsi'] = self._calculate_rsi(data)

        # Calculate Moving Averages
        results['sma'] = self._calculate_sma(data)
        results['ema'] = self._calculate_ema(data)

        # Generate signals
        results['signals'] = self._generate_signals(results)

        return results

    def _calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> float:
        delta = data['Avg Price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0

    def _calculate_sma(self, data: pd.DataFrame, period: int = 20) -> float:
        sma = data['Avg Price'].rolling(window=period).mean()
        return float(sma.iloc[-1]) if not pd.isna(sma.iloc[-1]) else float(data['Avg Price'].iloc[-1])

    def _calculate_ema(self, data: pd.DataFrame, period: int = 20) -> float:
        ema = data['Avg Price'].ewm(span=period, adjust=False).mean()
        return float(ema.iloc[-1]) if not pd.isna(ema.iloc[-1]) else float(data['Avg Price'].iloc[-1])

    def _generate_signals(self, results: dict) -> str:
        if results['rsi'] > 70:
            return 'SELL'
        elif results['rsi'] < 30:
            return 'BUY'
        return 'HOLD'
