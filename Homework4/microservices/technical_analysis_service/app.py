from flask import Flask
from routes.analysis_routes import analysis_bp

app = Flask(__name__)
app.register_blueprint(analysis_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
