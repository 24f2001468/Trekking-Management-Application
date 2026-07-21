from flask import Flask
# pyrefly: ignore [missing-import]
from flask_cors import CORS
# pyrefly: ignore [missing-import]
from flask_jwt_extended import JWTManager
from models.database import db
from models.models import User, StaffProfile, Trek, Booking
import os
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    
    # Configuration
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'tma.sqlite3')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'super-secret-tma-key-123' # In production, use env var
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
    
    # Initialize plugins
    CORS(app)
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Register blueprints
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
