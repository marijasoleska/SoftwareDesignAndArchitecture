from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Service URLs using docker-compose service names
TECHNICAL_SERVICE_URL = 'http://technical_analysis_service:5001'
FUNDAMENTAL_SERVICE_URL = 'http://fundamental_analysis_service:5003'
LSTM_SERVICE_URL = 'http://lstm_prediction_service:5002'
SCRAPING_SERVICE_URL = 'http://scraping_service:5004'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/companies', methods=['GET'])
def get_companies():
    try:
        response = requests.get(f'{SCRAPING_SERVICE_URL}/api/scraper/companies')
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/scrape', methods=['POST'])
def scrape_data():
    try:
        response = requests.post(f'{SCRAPING_SERVICE_URL}/api/scraper/refresh')
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        results = {}

        # Get technical analysis
        tech_response = requests.post(
            f'{TECHNICAL_SERVICE_URL}/api/technical/analyze',
            json=data
        )
        results['technical'] = tech_response.json()

        # Get fundamental analysis
        fund_response = requests.post(
            f'{FUNDAMENTAL_SERVICE_URL}/api/fundamental/analyze',
            json=data
        )
        results['fundamental'] = fund_response.json()

        # Get LSTM predictions
        lstm_response = requests.post(
            f'{LSTM_SERVICE_URL}/api/lstm/predict',
            json=data
        )
        results['prediction'] = lstm_response.json()

        return jsonify(results)
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)