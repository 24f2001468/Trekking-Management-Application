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
    
    # Initialize Celery
    from celery_app import celery_instance
    celery_instance.conf.update(app.config)
    class ContextTask(celery_instance.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery_instance.Task = ContextTask

    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.staff import staff_bp
    from routes.trekker import trekker_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(staff_bp, url_prefix='/api/staff')
    app.register_blueprint(trekker_bp, url_prefix='/api/trekker')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
