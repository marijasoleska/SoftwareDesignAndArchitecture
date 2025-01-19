def validate_stock_data(data):
    """Validates the input stock data."""
    if not data or 'historical_data' not in data:
        raise ValueError("No historical data provided")

    required_fields = ['Date', 'Last trade price']
    if not data['historical_data'] or not all(
            field in data['historical_data'][0] for field in required_fields
    ):
        raise ValueError(f"Missing required fields: {required_fields}")

    if len(data['historical_data']) < 2:
        raise ValueError("Insufficient data points. Need at least 2 data points")