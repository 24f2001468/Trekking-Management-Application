from app import create_app
from models.database import db
from models.models import User
from werkzeug.security import generate_password_hash

def init_database():
    app = create_app()
    with app.app_context():
        # Create tables
        db.create_all()
        # Ensure price column exists (SQLite tolerant)
        try:
            db.session.execute('ALTER TABLE treks ADD COLUMN price FLOAT')
        except Exception:
            pass
        # Backfill dynamic price for existing treks
        from models.models import Trek
        for trek in Trek.query.all():
            if trek.price is None:
                trek.price = trek.calculate_price()
        db.session.commit()
        print("Database tables created.")
        
        # Check if Admin already exists
        admin = User.query.filter_by(role='Admin').first()
        if not admin:
            # Create the superuser/admin programmatically
            admin_user = User(
                username='admin',
                email='admin@tma.com',
                password_hash=generate_password_hash('admin123'),
                role='Admin',
                active=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully.")
        else:
            print("Admin user already exists.")

if __name__ == '__main__':
    init_database()
