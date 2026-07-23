from flask import Blueprint, request, jsonify
# pyrefly: ignore [missing-import]
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.database import db
from models.models import User, StaffProfile, Trek, Booking
from werkzeug.security import generate_password_hash
from datetime import datetime

admin_bp = Blueprint('admin_bp', __name__)

def admin_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        if identity.get('role') != 'Admin':
            return jsonify({"msg": "Admin access required"}), 403
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

@admin_bp.route('/dashboard_stats', methods=['GET'])
@admin_required
def get_stats():
    stats = {
        'total_treks': Trek.query.count(),
        'total_users': User.query.filter_by(role='Trekker').count(),
        'total_staff': StaffProfile.query.count(),
        'total_bookings': Booking.query.count()
    }
    return jsonify(stats), 200

# User Management
@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    users = User.query.filter_by(role='Trekker').all()
    return jsonify([user.to_dict() for user in users]), 200

@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'Admin':
        return jsonify({"msg": "Cannot modify Admin status"}), 400
    user.active = not user.active
    db.session.commit()
    return jsonify(user.to_dict()), 200

# Staff Management
@admin_bp.route('/staff', methods=['GET'])
@admin_required
def get_staff():
    staff = StaffProfile.query.all()
    return jsonify([s.to_dict() for s in staff]), 200

@admin_bp.route('/staff', methods=['POST'])
@admin_required
def add_staff():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password') or not data.get('name'):
        return jsonify({"msg": "Missing required fields"}), 400
    
    if User.query.filter_by(username=data['username']).first() or (data.get('email') and User.query.filter_by(email=data['email']).first()):
        return jsonify({"msg": "Username or Email already exists"}), 409
        
    new_user = User(
        username=data['username'],
        email=data.get('email', f"{data['username']}@tma.com"),
        password_hash=generate_password_hash(data['password']),
        role='Trek Staff',
        active=True
    )
    db.session.add(new_user)
    db.session.flush() # Get new_user.id
    
    new_staff = StaffProfile(
        user_id=new_user.id,
        name=data['name'],
        contact_details=data.get('contact_details', '')
    )
    db.session.add(new_staff)
    db.session.commit()
    return jsonify(new_staff.to_dict()), 201

@admin_bp.route('/staff/<int:staff_id>/status', methods=['PUT'])
@admin_required
def toggle_staff_status(staff_id):
    staff = StaffProfile.query.get_or_404(staff_id)
    staff.status = 'Inactive' if staff.status == 'Active' else 'Active'
    staff.user.active = (staff.status == 'Active')
    db.session.commit()
    return jsonify(staff.to_dict()), 200

# Treks Management
@admin_bp.route('/treks', methods=['GET'])
@admin_required
def get_treks():
    treks = Trek.query.all()
    return jsonify([t.to_dict() for t in treks]), 200

@admin_bp.route('/treks', methods=['POST'])
@admin_required
def create_trek():
    data = request.get_json()
    try:
        new_trek = Trek(
            name=data['name'],
            location=data['location'],
            difficulty=data['difficulty'],
            duration=int(data['duration']),
            available_slots=int(data['available_slots']),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
            status=data.get('status', 'Open')
        )
        db.session.add(new_trek)
        db.session.commit()
        return jsonify(new_trek.to_dict()), 201
    except Exception as e:
        return jsonify({"msg": str(e)}), 400

@admin_bp.route('/treks/<int:trek_id>', methods=['PUT'])
@admin_required
def update_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    data = request.get_json()
    try:
        if 'name' in data: trek.name = data['name']
        if 'location' in data: trek.location = data['location']
        if 'difficulty' in data: trek.difficulty = data['difficulty']
        if 'duration' in data: trek.duration = int(data['duration'])
        if 'available_slots' in data: trek.available_slots = int(data['available_slots'])
        if 'start_date' in data: trek.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        if 'end_date' in data: trek.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        if 'status' in data: trek.status = data['status']
        db.session.commit()
        return jsonify(trek.to_dict()), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 400

@admin_bp.route('/treks/<int:trek_id>', methods=['DELETE'])
@admin_required
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    db.session.delete(trek)
    db.session.commit()
    return jsonify({"msg": "Trek deleted"}), 200

@admin_bp.route('/treks/<int:trek_id>/assign', methods=['PUT'])
@admin_required
def assign_staff(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    data = request.get_json()
    staff_id = data.get('staff_id')
    if staff_id:
        staff = StaffProfile.query.get_or_404(staff_id)
        trek.assigned_staff_id = staff.id
    else:
        trek.assigned_staff_id = None
    db.session.commit()
    return jsonify(trek.to_dict()), 200

# Bookings Management
@admin_bp.route('/bookings', methods=['GET'])
@admin_required
def get_bookings():
    bookings = Booking.query.all()
    return jsonify([b.to_dict() for b in bookings]), 200
