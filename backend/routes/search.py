from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models.database import db
from models.models import Trek, Booking
from datetime import datetime
import functools

trek_search_bp = Blueprint('trek_search_bp', __name__)

def admin_required(fn):
    @functools.wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if not claims or claims.get('role') != 'Admin':
            return jsonify({"msg": "Admin authorization required"}), 403
        return fn(*args, **kwargs)
    return wrapper

def staff_or_admin_required(fn):
    @functools.wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if not claims or claims.get('role') not in ('Admin', 'Trek Staff'):
            return jsonify({"msg": "Staff or Admin authorization required"}), 403
        return fn(*args, **kwargs)
    return wrapper

@trek_search_bp.route('/search', methods=['GET'])
@staff_or_admin_required
def search_treks():
    search_term = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()
    difficulty_filter = request.args.get('difficulty', '').strip()
    staff_filter = request.args.get('staff_id', '').strip()
    start_date_str = request.args.get('from_date', '').strip()
    end_date_str = request.args.get('to_date', '').strip()

    query = Trek.query
    if search_term:
        match_pattern = f'%{search_term}%'
        query = query.filter(db.or_(Trek.name.ilike(match_pattern), Trek.location.ilike(match_pattern)))
    if status_filter:
        query = query.filter_by(status=status_filter)
    if difficulty_filter:
        query = query.filter_by(difficulty=difficulty_filter)
    if staff_filter:
        query = query.filter_by(assigned_staff_id=int(staff_filter))
    if start_date_str:
        try:
            parsed_start = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(Trek.start_date >= parsed_start)
        except ValueError:
            return jsonify({"msg": "Invalid from_date. Expected format YYYY-MM-DD"}), 400
    if end_date_str:
        try:
            parsed_end = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(Trek.end_date <= parsed_end)
        except ValueError:
            return jsonify({"msg": "Invalid to_date. Expected format YYYY-MM-DD"}), 400

    treks_list = query.order_by(Trek.start_date.asc()).all()
    search_results = []
    for item in treks_list:
        data = item.to_dict()
        data['participants_count'] = Booking.query.filter_by(trek_id=item.id, status='Booked').count()
        search_results.append(data)
    return jsonify(search_results), 200

@trek_search_bp.route('/<int:trek_id>/summary', methods=['GET'])
@admin_required
def get_trek_summary(trek_id):
    target_trek = Trek.query.get_or_404(trek_id)
    summary_data = target_trek.to_dict()
    booking_records = Booking.query.filter_by(trek_id=trek_id).all()
    
    summary_data['booking_stats'] = {
        'total': len(booking_records),
        'booked': sum(1 for item in booking_records if item.status == 'Booked'),
        'cancelled': sum(1 for item in booking_records if item.status == 'Cancelled'),
        'completed': sum(1 for item in booking_records if item.status == 'Completed'),
        'paid': sum(1 for item in booking_records if item.payment_status == 'Paid'),
        'payment_pending': sum(1 for item in booking_records if item.payment_status == 'Pending'),
    }
    return jsonify(summary_data), 200
