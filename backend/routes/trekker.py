from flask import Blueprint, request, jsonify
# pyrefly: ignore [missing-import]
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import db
from models.models import User, Trek, Booking
from cache import cache
import functools
from datetime import datetime

trekker_bp = Blueprint('trekker_bp', __name__)

def trekker_required(fn):
    @functools.wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if not claims or claims.get('role') != 'Trekker':
            return jsonify({"msg": "Trekker access required"}), 403
        return fn(*args, **kwargs)
    return wrapper

@trekker_bp.route('/treks/open', methods=['GET'])
@trekker_required
@cache.cached(timeout=300, key_prefix='open_treks')
def get_open_treks():
    treks = Trek.query.filter_by(status='Open').all()
    treks_data = []
    for t in treks:
        t_dict = t.to_dict()
        t_dict['participants_count'] = Booking.query.filter_by(trek_id=t.id, status='Booked').count()
        treks_data.append(t_dict)
    return jsonify(treks_data), 200

@trekker_bp.route('/bookings', methods=['POST'])
@trekker_required
def book_trek():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    trek_id = data.get('trek_id')
    if not trek_id:
        return jsonify({"msg": "Missing trek ID"}), 400

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"msg": "Trek not found"}), 404
    if trek.status != 'Open':
        return jsonify({"msg": "Trek is not open for booking"}), 400
    if datetime.utcnow().date() > trek.end_date:
        return jsonify({"msg": "Trek booking period has ended"}), 400
    if trek.available_slots <= 0:
        return jsonify({"msg": "Trek slots are full"}), 400

    existing = Booking.query.filter_by(user_id=user_id, trek_id=trek_id)\
        .filter(Booking.status != 'Cancelled').first()
    if existing:
        return jsonify({"msg": "You have already booked this trek"}), 400

    new_booking = Booking(user_id=user_id, trek_id=trek_id, status='Booked', payment_status='Pending')
    trek.available_slots -= 1
    db.session.add(new_booking)
    db.session.commit()
    cache.delete('open_treks')
    return jsonify(new_booking.to_dict()), 201

@trekker_bp.route('/bookings', methods=['GET'])
@trekker_required
def get_my_bookings():
    user_id = int(get_jwt_identity())
    bookings = Booking.query.filter_by(user_id=user_id).all()
    return jsonify([b.to_dict() for b in bookings]), 200

@trekker_bp.route('/bookings/<int:booking_id>/cancel', methods=['PUT'])
@trekker_required
def cancel_booking(booking_id):
    user_id = int(get_jwt_identity())
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != user_id:
        return jsonify({"msg": "Unauthorized"}), 403
    if booking.status == 'Cancelled':
        return jsonify({"msg": "Booking is already cancelled"}), 400

    booking.status = 'Cancelled'
    if booking.trek:
        booking.trek.available_slots += 1
    db.session.commit()
    cache.delete('open_treks')
    return jsonify(booking.to_dict()), 200

@trekker_bp.route('/export', methods=['POST'])
@trekker_required
def export_history():
    """
    Trigger async CSV export via Celery task.
    Falls back to synchronous if Redis/Celery unavailable.
    """
    from tasks import export_user_history
    user_id = int(get_jwt_identity())
    try:
        # Try async Celery dispatch first (requires Redis)
        task = export_user_history.delay(user_id)
        return jsonify({"task_id": task.id}), 202
    except Exception:
        # Fallback: run synchronously if Celery/Redis not available
        csv_data = export_user_history(user_id)
        return jsonify({"state": "SUCCESS", "csv_data": csv_data}), 200

@trekker_bp.route('/export/<task_id>', methods=['GET'])
@trekker_required
def export_status(task_id):
    """Poll status of a Celery CSV export task."""
    from celery_app import celery_instance
    task_result = celery_instance.AsyncResult(task_id)
    if task_result.state == 'PENDING':
        return jsonify({"state": task_result.state, "msg": "Task is pending..."}), 200
    elif task_result.state == 'SUCCESS':
        return jsonify({"state": task_result.state, "csv_data": task_result.result}), 200
    else:
        return jsonify({"state": task_result.state, "msg": str(task_result.info)}), 200
