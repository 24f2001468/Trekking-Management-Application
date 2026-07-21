from flask import Flask
from models.database import db
from models.models import User, StaffProfile, Trek, Booking
import os

def create_app():
    app = Flask(__name__)
    
    # Configuration
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'tma.sqlite3')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize plugins
    db.init_app(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
