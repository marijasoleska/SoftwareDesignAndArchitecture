from flask import jsonify

def handle_analysis_error(error):
    error_message = str(error)
    if 'historical_data' in error_message:
        return jsonify({"error": error_message}), 400
    return jsonify({"error": "Internal server error"}), 500