import pandas as pd


class FundamentalAnalyzer:
    def analyze(self, data: pd.DataFrame) -> dict:
        try:
            # Calculate basic metrics
            avg_price = data['Last trade price'].mean()
            price_std = data['Last trade price'].std()
            total_volume = data['Volume'].sum() if 'Volume' in data.columns else 0

            # Analyze price movements
            movement_counter = self._analyze_stock_movement(data)
            recommendation = self._generate_recommendation(movement_counter)

            return {
                'average_price': round(avg_price, 2),
                'price_volatility': round(price_std, 2),
                'total_volume': total_volume,
                'price_movement_indicator': movement_counter,
                'recommendation': recommendation
            }

        except Exception as e:
            raise ValueError(f"Error performing fundamental analysis: {str(e)}")

    def _analyze_stock_movement(self, data: pd.DataFrame) -> int:
        movement_counter = 0
        prices = data['Last trade price'].values

        for i in range(1, len(prices)):
            if prices[i] < prices[i - 1]:
                movement_counter += 1
            elif prices[i] > prices[i - 1]:
                movement_counter -= 1

        return movement_counter

    def _generate_recommendation(self, movement_counter: int) -> str:
        if movement_counter > 0:
            return "BUY"
        elif movement_counter < 0:
            return "SELL"
        return "HOLD"
