from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from models.database import db
from models.models import Booking, Trek
from cache import cache
import functools

payments_bp = Blueprint('payments_bp', __name__)

def admin_required(fn):
    @functools.wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if not claims or claims.get('role') != 'Admin':
            return jsonify({"msg": "Admin authorization required"}), 403
        return fn(*args, **kwargs)
    return wrapper

@payments_bp.route('/bookings/<int:booking_id>/payment', methods=['PUT'])
@admin_required
def update_payment_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    payload = request.get_json() or {}
    new_payment_status = payload.get('payment_status')
    valid_statuses = ('Pending', 'Paid', 'Failed')
    
    if not new_payment_status or new_payment_status not in valid_statuses:
        return jsonify({"msg": f"Invalid payment status. Valid choices: {', '.join(valid_statuses)}"}), 400
        
    booking.payment_status = new_payment_status
    db.session.commit()
    return jsonify(booking.to_dict()), 200

@payments_bp.route('/bookings/<int:booking_id>/status', methods=['PUT'])
@admin_required
def update_booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    payload = request.get_json() or {}
    new_booking_status = payload.get('status')
    valid_statuses = ('Booked', 'Cancelled', 'Completed')
    
    if not new_booking_status or new_booking_status not in valid_statuses:
        return jsonify({"msg": f"Invalid booking status. Valid choices: {', '.join(valid_statuses)}"}), 400
        
    previous_status = booking.status
    booking.status = new_booking_status
    
    if new_booking_status == 'Cancelled' and previous_status == 'Booked' and booking.trek:
        booking.trek.available_slots += 1
        cache.delete('open_treks')
    elif new_booking_status == 'Booked' and previous_status == 'Cancelled' and booking.trek:
        if booking.trek.available_slots <= 0:
            return jsonify({"msg": "No available slots remaining for this trek"}), 400
        booking.trek.available_slots -= 1
        cache.delete('open_treks')
        
    db.session.commit()
    return jsonify(booking.to_dict()), 200

@payments_bp.route('/stats/revenue', methods=['GET'])
@admin_required
def get_revenue_stats():
    total_count = Booking.query.count()
    paid_count = Booking.query.filter_by(payment_status='Paid').count()
    pending_count = Booking.query.filter_by(payment_status='Pending').count()
    failed_count = Booking.query.filter_by(payment_status='Failed').count()
    
    return jsonify({
        "total_bookings": total_count,
        "paid": paid_count,
        "pending": pending_count,
        "failed": failed_count
    }), 200


# ── Trekker: confirm own payment after simulation ────────────────────────
@payments_bp.route('/bookings/<int:booking_id>/pay', methods=['PUT'])
@jwt_required()
def trekker_confirm_payment(booking_id):
    """
    Called by the trekker after a successful payment simulation.
    Only the booking owner can mark their own booking as Paid.
    """
    user_id = int(get_jwt_identity())
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != user_id:
        return jsonify({"msg": "Unauthorized — not your booking"}), 403

    if booking.payment_status == 'Paid':
        return jsonify(booking.to_dict()), 200  # idempotent

    payload = request.get_json() or {}
    result = payload.get('payment_status', 'Paid')
    if result not in ('Paid', 'Failed'):
        return jsonify({"msg": "Invalid payment result"}), 400

    booking.payment_status = result
    db.session.commit()
    return jsonify(booking.to_dict()), 200
