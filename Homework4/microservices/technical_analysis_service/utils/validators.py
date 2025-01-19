from flask import abort


def validate_historical_data(data):
    if not data or 'historical_data' not in data:
        abort(400, description="No historical data provided")

    required_fields = ['Date', 'Avg Price', 'Max', 'Min']
    for field in required_fields:
        if not all(field in record for record in data['historical_data']):
            abort(400, description=f"Missing required field: {field}")