def validate_stock_data(data):
    if not data or 'historical_data' not in data:
        raise ValueError("No historical data provided")

    if len(data['historical_data']) < 60:
        raise ValueError("Insufficient data points. Need at least 60 data points")

    required_fields = ['Last trade price']
    if not all(field in data['historical_data'][0] for field in required_fields):
        raise ValueError(f"Missing required fields: {required_fields}")