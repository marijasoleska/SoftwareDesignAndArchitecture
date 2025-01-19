from flask import Blueprint, request, jsonify
from ..services.scraper import StockScraper

scraper_bp = Blueprint('scraper', __name__)
scraper = StockScraper()

@scraper_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@scraper_bp.route('/api/scraper/companies', methods=['GET'])
def get_companies():
    try:
        companies = scraper.fetch_companies()
        return jsonify({"companies": companies}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@scraper_bp.route('/api/scraper/data/<company>', methods=['GET'])
def get_company_data(company):
    try:
        years = request.args.get('years', default=10, type=int)
        data = scraper.fetch_data_for_company(company, years)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@scraper_bp.route('/api/scraper/refresh', methods=['POST'])
def refresh_data():
    try:
        years = request.json.get('years', 10)
        results = scraper.fetch_all_companies_data(years)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500