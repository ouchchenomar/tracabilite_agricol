from flask import Flask
from flask_cors import CORS
from config import Config
from app.models import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Activer CORS
    CORS(app)
    
    db.init_app(app)
    
    # Importez et enregistrez les blueprints ici
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.route('/test')
    def test():
        return {'message': 'Le serveur fonctionne correctement'}
    
    return app