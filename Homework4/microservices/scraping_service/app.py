from flask import Flask
from routes.scraper_routes import scraper_bp

app = Flask(__name__)
app.register_blueprint(scraper_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)