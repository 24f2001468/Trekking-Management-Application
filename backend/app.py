from flask import Flask
# pyrefly: ignore [missing-import]
from flask_cors import CORS
# pyrefly: ignore [missing-import]
from flask_jwt_extended import JWTManager
from models.database import db
from models.models import User, StaffProfile, Trek, Booking
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

def create_app():
    app = Flask(__name__)

    # ── Configuration ────────────────────────────
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'tma.sqlite3')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # JWT – key must be at least 32 bytes for HS256
    app.config['JWT_SECRET_KEY'] = 'tma-super-secret-key-for-jwt-auth-2026!'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

    # Cache – Redis backend
    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300

    # ── Flask-Mail (configure via environment or change here) ──
    app.config['MAIL_SERVER']   = os.environ.get('MAIL_SERVER',   'smtp.gmail.com')
    app.config['MAIL_PORT']     = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS']  = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')  # set in .env
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')  # set in .env
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@tma.app')

    # ── Initialize extensions ─────────────────────
    CORS(app)
    db.init_app(app)
    JWTManager(app)

    from cache import cache
    cache.init_app(app)

    from mail import mail
    mail.init_app(app)

    # ── Celery context task (kept for CSV export compatibility) ──
    from celery_app import celery_instance

    class ContextTask(celery_instance.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_instance.Task = ContextTask

    # ── APScheduler (daily reminders + monthly report) ──
    from scheduler import init_scheduler
    init_scheduler(app)

    # ── Register blueprints ───────────────────────
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.staff import staff_bp
    from routes.trekker import trekker_bp
    from routes.payments import payments_bp
    from routes.search import trek_search_bp
    from routes.analytics import analytics_bp

    app.register_blueprint(auth_bp,        url_prefix='/api/auth')
    app.register_blueprint(admin_bp,       url_prefix='/api/admin')
    app.register_blueprint(staff_bp,       url_prefix='/api/staff')
    app.register_blueprint(trekker_bp,     url_prefix='/api/trekker')
    app.register_blueprint(payments_bp,    url_prefix='/api/admin')
    app.register_blueprint(trek_search_bp, url_prefix='/api/treks')
    app.register_blueprint(analytics_bp,   url_prefix='/api/analytics')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
