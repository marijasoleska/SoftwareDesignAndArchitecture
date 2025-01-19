from flask import Blueprint, request, jsonify
from ..services.technical_analyzer import TechnicalAnalyzer
import pandas as pd

analysis_bp = Blueprint('analysis', __name__)
analyzer = TechnicalAnalyzer()


@analysis_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200


@analysis_bp.route('/api/technical/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        if not data or 'historical_data' not in data:
            return jsonify({"error": "No historical data provided"}), 400

        df = pd.DataFrame(data['historical_data'])
        results = analyzer.analyze(df)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
