from abc import ABC, abstractmethod
import pandas as pd

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
