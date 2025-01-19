import pandas as pd
from flask import jsonify


def format_analysis_response(analysis_results, signal):
    latest_data = analysis_results.iloc[-1]

    response = {
        "signal": signal,
        "indicators": {
            name: float(value) if pd.notna(value) else None
            for name, value in latest_data.items()
        }
    }

    return jsonify(response), 200