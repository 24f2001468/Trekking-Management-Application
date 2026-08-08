from flask import Blueprint, request, jsonify
# pyrefly: ignore [missing-import]
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.database import db
from models.models import User, StaffProfile, Trek, Booking
from cache import cache
from werkzeug.security import generate_password_hash
from datetime import datetime
import functools

admin_bp = Blueprint('admin_bp', __name__)

def admin_required(fn):
    @functools.wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if not claims or claims.get('role') != 'Admin':
            return jsonify({"msg": "Admin access required"}), 403
        return fn(*args, **kwargs)
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
    """Temporarily deactivate / reactivate a user (reversible)."""
    user = User.query.get_or_404(user_id)
    if user.role == 'Admin':
        return jsonify({"msg": "Cannot modify Admin status"}), 400
    user.active = not user.active
    db.session.commit()
    return jsonify(user.to_dict()), 200

@admin_bp.route('/users/<int:user_id>/blacklist', methods=['PUT'])
@admin_required
def toggle_blacklist(user_id):
    """Permanently blacklist / unblacklist a user.
    A blacklisted user cannot log in regardless of active flag."""
    user = User.query.get_or_404(user_id)
    if user.role == 'Admin':
        return jsonify({"msg": "Cannot blacklist an Admin"}), 400
    user.is_blacklisted = not user.is_blacklisted
    if user.is_blacklisted:
        user.active = False  # also deactivate
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
        # Calculate and store dynamic price
        new_trek.price = new_trek.calculate_price()
        db.session.add(new_trek)
        db.session.commit()
        cache.delete('open_treks')
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
        trek.price = trek.calculate_price()
        db.session.commit()
        cache.delete('open_treks')
        return jsonify(trek.to_dict()), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 400

@admin_bp.route('/treks/<int:trek_id>', methods=['DELETE'])
@admin_required
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    db.session.delete(trek)
    db.session.commit()
    cache.delete('open_treks')
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
    cache.delete('open_treks')
    return jsonify(trek.to_dict()), 200

# Bookings Management
@admin_bp.route('/bookings', methods=['GET'])
@admin_required
def get_bookings():
    bookings = Booking.query.all()
    return jsonify([b.to_dict() for b in bookings]), 200

@admin_bp.route('/reports/monthly', methods=['GET'])
@admin_required
def get_monthly_report():
    """Return the monthly HTML report as a downloadable file."""
    from scheduler import generate_monthly_report
    from flask import Response, current_app
    # Trigger report generation inline and capture the HTML
    from datetime import datetime, timedelta
    from sqlalchemy import func

    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)

    recent_treks = Trek.query.filter(Trek.start_date >= thirty_days_ago).all()
    total_bookings = Booking.query.filter(
        Booking.booking_date >= thirty_days_ago,
        Booking.status != 'Cancelled'
    ).count()
    unique_participants = db.session.query(func.count(func.distinct(Booking.user_id))).filter(
        Booking.booking_date >= thirty_days_ago,
        Booking.status != 'Cancelled'
    ).scalar()

    top_treks_rows = (
        db.session.query(Trek.name, Trek.location, func.count(Booking.id).label('cnt'))
        .join(Booking, Booking.trek_id == Trek.id)
        .filter(Booking.booking_date >= thirty_days_ago, Booking.status != 'Cancelled')
        .group_by(Trek.id)
        .order_by(func.count(Booking.id).desc())
        .limit(5).all()
    )

    top_rows_html = ''.join(
        f"<tr><td style='padding:.5rem .75rem'>{r[0]}</td><td style='padding:.5rem .75rem'>{r[1]}</td>"
        f"<td style='padding:.5rem .75rem;text-align:center'>{r[2]}</td></tr>"
        for r in top_treks_rows
    ) or "<tr><td colspan='3' style='padding:.5rem;color:#7fa88c'>No data</td></tr>"

    trek_rows_html = ''.join(
        f"<tr><td style='padding:.4rem .75rem'>{t.name}</td><td style='padding:.4rem .75rem'>{t.location}</td>"
        f"<td style='padding:.4rem .75rem'>{t.status}</td><td style='padding:.4rem .75rem'>{t.start_date}</td></tr>"
        for t in recent_treks
    ) or "<tr><td colspan='4' style='padding:.5rem;color:#7fa88c'>No treks this period</td></tr>"

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>TMA Monthly Report — {now.strftime('%B %Y')}</title></head>
<body style="font-family:Arial,sans-serif;background:#0b1612;color:#e8f0ea;padding:2rem;margin:0;">
<div style="max-width:700px;margin:auto;background:#12201a;border-radius:14px;padding:2.5rem;border:1px solid rgba(61,139,101,0.2);">
  <h1 style="color:#6dbf95;margin-top:0;">📊 Monthly Activity Report — {now.strftime('%B %Y')}</h1>
  <p style="color:#7fa88c;">Period: <strong>{thirty_days_ago.strftime('%d %b %Y')}</strong> — <strong>{now.strftime('%d %b %Y')}</strong></p>
  <div style="display:flex;gap:1rem;margin:1.5rem 0;flex-wrap:wrap;">
    <div style="flex:1;min-width:140px;background:rgba(61,139,101,0.12);border-radius:10px;padding:1rem;text-align:center;">
      <div style="font-size:2rem;font-weight:800;color:#6dbf95;">{len(recent_treks)}</div>
      <div style="font-size:.8rem;color:#7fa88c;text-transform:uppercase;letter-spacing:.06em;">Treks Conducted</div>
    </div>
    <div style="flex:1;min-width:140px;background:rgba(63,143,160,0.12);border-radius:10px;padding:1rem;text-align:center;">
      <div style="font-size:2rem;font-weight:800;color:#7ec9d8;">{unique_participants}</div>
      <div style="font-size:.8rem;color:#7fa88c;text-transform:uppercase;letter-spacing:.06em;">Unique Participants</div>
    </div>
    <div style="flex:1;min-width:140px;background:rgba(212,146,74,0.12);border-radius:10px;padding:1rem;text-align:center;">
      <div style="font-size:2rem;font-weight:800;color:#e8ae72;">{total_bookings}</div>
      <div style="font-size:.8rem;color:#7fa88c;text-transform:uppercase;letter-spacing:.06em;">Total Bookings</div>
    </div>
  </div>
  <h3 style="color:#6dbf95;">🏆 Most Popular Treks</h3>
  <table style="width:100%;border-collapse:collapse;">
    <thead><tr style="background:rgba(0,0,0,0.3);">
      <th style="padding:.5rem .75rem;text-align:left;color:#4d6b58;font-size:.75rem;text-transform:uppercase;">Trek</th>
      <th style="padding:.5rem .75rem;text-align:left;color:#4d6b58;font-size:.75rem;text-transform:uppercase;">Location</th>
      <th style="padding:.5rem .75rem;text-align:center;color:#4d6b58;font-size:.75rem;text-transform:uppercase;">Bookings</th>
    </tr></thead>
    <tbody>{top_rows_html}</tbody>
  </table>
  <h3 style="color:#6dbf95;margin-top:1.5rem;">📋 All Treks This Period</h3>
  <table style="width:100%;border-collapse:collapse;">
    <thead><tr style="background:rgba(0,0,0,0.3);">
      <th style="padding:.5rem .75rem;text-align:left;color:#4d6b58;font-size:.75rem;text-transform:uppercase;">Name</th>
      <th style="padding:.5rem .75rem;text-align:left;color:#4d6b58;font-size:.75rem;text-transform:uppercase;">Location</th>
      <th style="padding:.5rem .75rem;text-align:left;color:#4d6b58;font-size:.75rem;text-transform:uppercase;">Status</th>
      <th style="padding:.5rem .75rem;text-align:left;color:#4d6b58;font-size:.75rem;text-transform:uppercase;">Start</th>
    </tr></thead>
    <tbody>{trek_rows_html}</tbody>
  </table>
  <hr style="border-color:rgba(61,139,101,0.15);margin:2rem 0 1rem;">
  <p style="font-size:.78rem;color:#4d6b58;">Generated {now.strftime('%d %b %Y %H:%M UTC')} &mdash; Trekking Management Application</p>
</div></body></html>"""

    return Response(
        html,
        mimetype='text/html',
        headers={'Content-Disposition': f'attachment; filename="tma-report-{now.strftime("%Y-%m")}.html"'}
    )
