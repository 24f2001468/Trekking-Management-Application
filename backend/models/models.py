from .database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'Admin', 'Trek Staff', 'Trekker'
    active = db.Column(db.Boolean, default=True)
    
    # Relationships
    staff_profile = db.relationship('StaffProfile', back_populates='user', uselist=False, cascade="all, delete-orphan")
    bookings = db.relationship('Booking', back_populates='user', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'active': self.active
        }

class StaffProfile(db.Model):
    __tablename__ = 'staff_profiles'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    contact_details = db.Column(db.String(150), nullable=True)
    status = db.Column(db.String(50), default='Active')
    
    # Relationships
    user = db.relationship('User', back_populates='staff_profile')
    assigned_treks = db.relationship('Trek', back_populates='staff')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'contact_details': self.contact_details,
            'status': self.status,
            'user': self.user.to_dict() if self.user else None
        }

class Trek(db.Model):
    __tablename__ = 'treks'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False) # Easy, Moderate, Hard
    duration = db.Column(db.Integer, nullable=False) # in days
    available_slots = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='Pending') # Pending, Approved, Open, Closed, Completed
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('staff_profiles.id'), nullable=True)
    
    # Relationships
    staff = db.relationship('StaffProfile', back_populates='assigned_treks')
    bookings = db.relationship('Booking', back_populates='trek', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'difficulty': self.difficulty,
            'duration': self.duration,
            'available_slots': self.available_slots,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'assigned_staff_id': self.assigned_staff_id,
            'staff': {'id': self.staff.id, 'name': self.staff.name} if self.staff else None
        }

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Booked') # Booked, Cancelled, Completed
    payment_status = db.Column(db.String(50), default='Pending') # Pending, Paid, Failed
    
    # Relationships
    user = db.relationship('User', back_populates='bookings')
    trek = db.relationship('Trek', back_populates='bookings')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'trek_id': self.trek_id,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'status': self.status,
            'payment_status': self.payment_status,
            'user': self.user.to_dict() if self.user else None,
            'trek': {'id': self.trek.id, 'name': self.trek.name} if self.trek else None
        }
