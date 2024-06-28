from flask import Flask
from flask_cors import CORS
from views.api import bp as views_bp
from settings import settings

def create_app():
    app = Flask(__name__)
    
    CORS(app, resources={r"/*": {"origins": "*"}})

    app.config.from_object(settings)
    app.register_blueprint(views_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5010)
