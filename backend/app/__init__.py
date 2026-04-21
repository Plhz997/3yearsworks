from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config.config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, supports_credentials=True)
    
    @app.before_request
    def log_request():
        auth_header = request.headers.get('Authorization', 'Not present')
        print(f"Request: {request.method} {request.path}")
        print(f"Authorization header: {auth_header}")
    
    from api.auth import auth_bp
    from api.test import test_bp
    from api.vocabulary import vocab_bp
    from api.admin import admin_bp
    from api.user import user_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(test_bp, url_prefix='/api/test')
    app.register_blueprint(vocab_bp, url_prefix='/api/vocab')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    
    return app