from flask import Blueprint, request, jsonify
# pyrefly: ignore [missing-import]
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.database import db
from models.models import User, Trek, Booking
from cache import cache

trekker_bp = Blueprint('trekker_bp', __name__)

def trekker_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        if identity.get('role') != 'Trekker':
            return jsonify({"msg": "Trekker access required"}), 403
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

@trekker_bp.route('/treks/open', methods=['GET'])
@trekker_required
@cache.cached(timeout=300, key_prefix='open_treks')
def get_open_treks():
    # Only return treks that are 'Open'
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
    identity = get_jwt_identity()
    user_id = identity.get('id')
    data = request.get_json()
    
    trek_id = data.get('trek_id')
    if not trek_id:
        return jsonify({"msg": "Missing trek ID"}), 400
        
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"msg": "Trek not found"}), 404
        
    if trek.status != 'Open':
        return jsonify({"msg": "Trek is not open for booking"}), 400
        
    if trek.available_slots <= 0:
        return jsonify({"msg": "Trek slots are full"}), 400
        
    # Check for duplicate booking
    existing_booking = Booking.query.filter_by(user_id=user_id, trek_id=trek_id).filter(Booking.status != 'Cancelled').first()
    if existing_booking:
        return jsonify({"msg": "You have already booked this trek"}), 400
        
    # Create booking
    new_booking = Booking(
        user_id=user_id,
        trek_id=trek_id,
        status='Booked',
        payment_status='Pending'
    )
    
    # Decrement available slots
    trek.available_slots -= 1
    
    db.session.add(new_booking)
    db.session.commit()
    
    # Invalidate open_treks cache since available slots changed
    cache.delete('open_treks')
    
    return jsonify(new_booking.to_dict()), 201

@trekker_bp.route('/bookings', methods=['GET'])
@trekker_required
def get_my_bookings():
    identity = get_jwt_identity()
    user_id = identity.get('id')
    bookings = Booking.query.filter_by(user_id=user_id).all()
    return jsonify([b.to_dict() for b in bookings]), 200

@trekker_bp.route('/bookings/<int:booking_id>/cancel', methods=['PUT'])
@trekker_required
def cancel_booking(booking_id):
    identity = get_jwt_identity()
    user_id = identity.get('id')
    
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != user_id:
        return jsonify({"msg": "Unauthorized"}), 403
        
    if booking.status == 'Cancelled':
        return jsonify({"msg": "Booking is already cancelled"}), 400
        
    booking.status = 'Cancelled'
    
    # Increment available slots
    if booking.trek:
        booking.trek.available_slots += 1
        
    db.session.commit()
    
    # Invalidate open_treks cache since available slots changed
    cache.delete('open_treks')
    
    return jsonify(booking.to_dict()), 200

@trekker_bp.route('/export', methods=['POST'])
@trekker_required
def export_history():
    from tasks import export_user_history
    identity = get_jwt_identity()
    user_id = identity.get('id')
    
    # Trigger Celery Task
    task = export_user_history.delay(user_id)
    return jsonify({"task_id": task.id}), 202

@trekker_bp.route('/export/<task_id>', methods=['GET'])
@trekker_required
def export_status(task_id):
    from celery_app import celery_instance
    task_result = celery_instance.AsyncResult(task_id)
    
    if task_result.state == 'PENDING':
        return jsonify({"state": task_result.state, "msg": "Task is pending..."}), 200
    elif task_result.state == 'SUCCESS':
        return jsonify({
            "state": task_result.state,
            "csv_data": task_result.result
        }), 200
    else:
        return jsonify({"state": task_result.state, "msg": str(task_result.info)}), 200
