from flask import Blueprint, jsonify
# pyrefly: ignore [missing-import]
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import db
from models.models import Trek, Booking, User
from cache import cache
from datetime import datetime, timedelta
from sqlalchemy import func
import functools

analytics_bp = Blueprint('analytics_bp', __name__)

def admin_required(fn):
    @functools.wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if not claims or claims.get('role') != 'Admin':
            return jsonify({"msg": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


# ── PUBLIC (no auth) ──────────────────────────────────────

@analytics_bp.route('/public/stats', methods=['GET'])
def public_stats():
    total_treks     = Trek.query.count()
    open_treks      = Trek.query.filter_by(status='Open').count()
    completed_treks = Trek.query.filter_by(status='Completed').count()
    total_trekkers  = User.query.filter_by(role='Trekker', active=True).count()
    total_bookings  = Booking.query.filter(Booking.status != 'Cancelled').count()

    difficulty_rows = (
        db.session.query(Trek.difficulty, func.count(Trek.id))
        .group_by(Trek.difficulty).all()
    )
    difficulty_breakdown = {r[0]: r[1] for r in difficulty_rows}

    top_treks_rows = (
        db.session.query(Trek.name, func.count(Booking.id).label('cnt'))
        .join(Booking, Booking.trek_id == Trek.id)
        .filter(Booking.status != 'Cancelled')
        .group_by(Trek.id, Trek.name)
        .order_by(func.count(Booking.id).desc())
        .limit(5).all()
    )
    top_treks = [{"name": r[0], "bookings": r[1]} for r in top_treks_rows]

    status_rows = (
        db.session.query(Trek.status, func.count(Trek.id))
        .group_by(Trek.status).all()
    )
    status_breakdown = {r[0]: r[1] for r in status_rows}

    return jsonify({
        "total_treks":          total_treks,
        "open_treks":           open_treks,
        "completed_treks":      completed_treks,
        "total_trekkers":       total_trekkers,
        "total_bookings":       total_bookings,
        "difficulty_breakdown": difficulty_breakdown,
        "top_treks":            top_treks,
        "status_breakdown":     status_breakdown,
    }), 200


# ── ADMIN (JWT required) ──────────────────────────────────

@analytics_bp.route('/admin/overview', methods=['GET'])
@admin_required
def admin_overview():
    twelve_months_ago = datetime.utcnow() - timedelta(days=365)

    monthly_rows = (
        db.session.query(
            func.strftime('%Y-%m', Booking.booking_date).label('month'),
            func.count(Booking.id).label('cnt')
        )
        .filter(Booking.booking_date >= twelve_months_ago)
        .group_by(func.strftime('%Y-%m', Booking.booking_date))
        .order_by(func.strftime('%Y-%m', Booking.booking_date))
        .all()
    )
    monthly_bookings = [{"month": r[0], "bookings": r[1]} for r in monthly_rows]

    top_treks_rows = (
        db.session.query(Trek.name, Trek.location, func.count(Booking.id).label('cnt'))
        .join(Booking, Booking.trek_id == Trek.id)
        .filter(Booking.status != 'Cancelled')
        .group_by(Trek.id, Trek.name, Trek.location)
        .order_by(func.count(Booking.id).desc())
        .limit(10).all()
    )
    top_treks = [{"name": r[0], "location": r[1], "participants": r[2]} for r in top_treks_rows]

    diff_rows = (
        db.session.query(Trek.difficulty, func.count(Booking.id).label('cnt'))
        .join(Booking, Booking.trek_id == Trek.id)
        .filter(Booking.status != 'Cancelled')
        .group_by(Trek.difficulty).all()
    )
    difficulty_dist = {r[0]: r[1] for r in diff_rows}

    status_rows = (
        db.session.query(Booking.status, func.count(Booking.id))
        .group_by(Booking.status).all()
    )
    booking_status_dist = {r[0]: r[1] for r in status_rows}

    payment_rows = (
        db.session.query(Booking.payment_status, func.count(Booking.id))
        .group_by(Booking.payment_status).all()
    )
    payment_dist = {r[0]: r[1] for r in payment_rows}

    monthly_participation_rows = (
        db.session.query(
            func.strftime('%Y-%m', Booking.booking_date).label('month'),
            func.count(func.distinct(Booking.user_id)).label('participants')
        )
        .filter(
            Booking.booking_date >= twelve_months_ago,
            Booking.status != 'Cancelled'
        )
        .group_by(func.strftime('%Y-%m', Booking.booking_date))
        .order_by(func.strftime('%Y-%m', Booking.booking_date))
        .all()
    )
    monthly_participation = [{"month": r[0], "participants": r[1]} for r in monthly_participation_rows]

    trek_status_rows = (
        db.session.query(Trek.status, func.count(Trek.id))
        .group_by(Trek.status).all()
    )
    trek_status_dist = {r[0]: r[1] for r in trek_status_rows}

    return jsonify({
        "monthly_bookings":           monthly_bookings,
        "top_treks":                  top_treks,
        "difficulty_distribution":    difficulty_dist,
        "booking_status_distribution": booking_status_dist,
        "payment_distribution":       payment_dist,
        "monthly_participation":      monthly_participation,
        "trek_status_distribution":   trek_status_dist,
    }), 200


@analytics_bp.route('/admin/trek/<int:trek_id>', methods=['GET'])
@admin_required
def trek_analytics(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    bookings = Booking.query.filter_by(trek_id=trek_id).all()
    status_dist  = {}
    payment_dist = {}
    for b in bookings:
        status_dist[b.status]           = status_dist.get(b.status, 0) + 1
        payment_dist[b.payment_status]  = payment_dist.get(b.payment_status, 0) + 1
    return jsonify({
        "trek":           trek.to_dict(),
        "total_bookings": len(bookings),
        "booking_status": status_dist,
        "payment_status": payment_dist,
        "fill_rate": round(
            (status_dist.get('Booked', 0) /
             max((trek.available_slots + status_dist.get('Booked', 0)), 1)) * 100, 1
        )
    }), 200
