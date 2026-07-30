from flask import Blueprint, request, jsonify
# pyrefly: ignore [missing-import]
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.database import db
from models.models import User, StaffProfile, Trek, Booking
from cache import cache

staff_bp = Blueprint('staff_bp', __name__)

def staff_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        if identity.get('role') != 'Trek Staff':
            return jsonify({"msg": "Staff access required"}), 403
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

@staff_bp.route('/treks', methods=['GET'])
@staff_required
def get_assigned_treks():
    identity = get_jwt_identity()
    user_id = identity.get('id')
    
    staff_profile = StaffProfile.query.filter_by(user_id=user_id).first()
    if not staff_profile:
        return jsonify({"msg": "Staff profile not found"}), 404
        
    treks = Trek.query.filter_by(assigned_staff_id=staff_profile.id).all()
    
    treks_data = []
    for t in treks:
        t_dict = t.to_dict()
        t_dict['participants_count'] = Booking.query.filter_by(trek_id=t.id).count()
        treks_data.append(t_dict)
        
    return jsonify(treks_data), 200

@staff_bp.route('/treks/<int:trek_id>', methods=['GET'])
@staff_required
def get_trek(trek_id):
    identity = get_jwt_identity()
    user_id = identity.get('id')
    staff_profile = StaffProfile.query.filter_by(user_id=user_id).first()
    
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != staff_profile.id:
        return jsonify({"msg": "Unauthorized: Not assigned to this trek"}), 403
        
    t_dict = trek.to_dict()
    t_dict['participants_count'] = Booking.query.filter_by(trek_id=trek.id).count()
    
    return jsonify(t_dict), 200

@staff_bp.route('/treks/<int:trek_id>', methods=['PUT'])
@staff_required
def update_trek(trek_id):
    identity = get_jwt_identity()
    staff_profile = StaffProfile.query.filter_by(user_id=identity.get('id')).first()
    
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != staff_profile.id:
        return jsonify({"msg": "Unauthorized: Not assigned to this trek"}), 403
        
    data = request.get_json()
    if 'status' in data:
        trek.status = data['status']
    if 'available_slots' in data:
        trek.available_slots = int(data['available_slots'])
        
    db.session.commit()
    cache.delete('open_treks')
    return jsonify(trek.to_dict()), 200

@staff_bp.route('/treks/<int:trek_id>/participants', methods=['GET'])
@staff_required
def get_participants(trek_id):
    identity = get_jwt_identity()
    staff_profile = StaffProfile.query.filter_by(user_id=identity.get('id')).first()
    
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != staff_profile.id:
        return jsonify({"msg": "Unauthorized: Not assigned to this trek"}), 403
        
    bookings = Booking.query.filter_by(trek_id=trek_id).all()
    return jsonify([b.to_dict() for b in bookings]), 200

@staff_bp.route('/bookings/<int:booking_id>/status', methods=['PUT'])
@staff_required
def update_booking_status(booking_id):
    identity = get_jwt_identity()
    staff_profile = StaffProfile.query.filter_by(user_id=identity.get('id')).first()
    
    booking = Booking.query.get_or_404(booking_id)
    if booking.trek.assigned_staff_id != staff_profile.id:
        return jsonify({"msg": "Unauthorized: Not assigned to this trek"}), 403
        
    data = request.get_json()
    if 'status' in data:
        booking.status = data['status']
    
    db.session.commit()
    return jsonify(booking.to_dict()), 200
