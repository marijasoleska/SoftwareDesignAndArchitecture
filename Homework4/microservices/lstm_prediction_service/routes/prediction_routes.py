from flask import Blueprint, request, jsonify
from ..services.lstm_model import LSTMPredictor
import pandas as pd

prediction_bp = Blueprint('prediction', __name__)
predictor = LSTMPredictor()


@prediction_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200


@prediction_bp.route('/api/lstm/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data or 'historical_data' not in data:
            return jsonify({"error": "No historical data provided"}), 400

        df = pd.DataFrame(data['historical_data'])
        predictions = predictor.predict(df)
        return jsonify(predictions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500