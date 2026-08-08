from flask import Blueprint, request, jsonify
# pyrefly: ignore [missing-import]
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import db
from models.models import User, StaffProfile, Trek, Booking
from cache import cache
import functools

staff_bp = Blueprint('staff_bp', __name__)

def staff_required(fn):
    @functools.wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if not claims or claims.get('role') != 'Trek Staff':
            return jsonify({"msg": "Staff access required"}), 403
        return fn(*args, **kwargs)
    return wrapper

def _get_staff_profile():
    user_id = int(get_jwt_identity())
    return StaffProfile.query.filter_by(user_id=user_id).first()

@staff_bp.route('/treks', methods=['GET'])
@staff_required
def get_assigned_treks():
    staff_profile = _get_staff_profile()
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
    staff_profile = _get_staff_profile()
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != staff_profile.id:
        return jsonify({"msg": "Unauthorized: Not assigned to this trek"}), 403
    t_dict = trek.to_dict()
    t_dict['participants_count'] = Booking.query.filter_by(trek_id=trek.id).count()
    return jsonify(t_dict), 200

@staff_bp.route('/treks/<int:trek_id>', methods=['PUT'])
@staff_required
def update_trek(trek_id):
    staff_profile = _get_staff_profile()
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
    staff_profile = _get_staff_profile()
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != staff_profile.id:
        return jsonify({"msg": "Unauthorized: Not assigned to this trek"}), 403
    bookings = Booking.query.filter_by(trek_id=trek_id).all()
    return jsonify([b.to_dict() for b in bookings]), 200

@staff_bp.route('/bookings/<int:booking_id>/status', methods=['PUT'])
@staff_required
def update_booking_status(booking_id):
    staff_profile = _get_staff_profile()
    booking = Booking.query.get_or_404(booking_id)
    if booking.trek.assigned_staff_id != staff_profile.id:
        return jsonify({"msg": "Unauthorized: Not assigned to this trek"}), 403
    data = request.get_json()
    if 'status' in data:
        booking.status = data['status']
    db.session.commit()
    return jsonify(booking.to_dict()), 200
