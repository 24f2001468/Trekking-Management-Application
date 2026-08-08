from flask import Blueprint, request, jsonify
from models.database import db
from models.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import functools, re

auth_bp = Blueprint('auth_bp', __name__)

# ── helpers ──────────────────────────────────────────────

def _valid_email(email):
    return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email))

def login_required(fn):
    @functools.wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper

# ── Register ─────────────────────────────────────────────

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = (data.get('username') or '').strip()
    email    = (data.get('email')    or '').strip().lower()
    password =  data.get('password') or ''

    if not username or not email or not password:
        return jsonify({"msg": "All fields are required"}), 400
    if len(username) < 3:
        return jsonify({"msg": "Username must be at least 3 characters"}), 400
    if not _valid_email(email):
        return jsonify({"msg": "Invalid email address"}), 400
    if len(password) < 6:
        return jsonify({"msg": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already taken"}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already registered"}), 409

    new_user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role='Trekker',
        active=True,
        is_blacklisted=False
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "Account created successfully"}), 201


# ── Login ─────────────────────────────────────────────────

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(username=data['username'].strip()).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({"msg": "Invalid username or password"}), 401

    if user.is_blacklisted:
        return jsonify({"msg": "Your account has been permanently suspended. Contact support."}), 403
    if not user.active:
        return jsonify({"msg": "Your account is currently inactive. Contact an administrator."}), 403

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role, 'username': user.username}
    )
    return jsonify({
        "access_token": access_token,
        "user": {"id": user.id, "username": user.username, "role": user.role, "email": user.email}
    }), 200


# ── Profile: GET own profile ──────────────────────────────

@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


# ── Profile: UPDATE own profile ───────────────────────────

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}

    # Username update
    if 'username' in data:
        new_username = data['username'].strip()
        if len(new_username) < 3:
            return jsonify({"msg": "Username must be at least 3 characters"}), 400
        if new_username != user.username:
            if User.query.filter_by(username=new_username).first():
                return jsonify({"msg": "Username already taken"}), 409
            user.username = new_username

    # Email update
    if 'email' in data:
        new_email = data['email'].strip().lower()
        if not _valid_email(new_email):
            return jsonify({"msg": "Invalid email address"}), 400
        if new_email != user.email:
            if User.query.filter_by(email=new_email).first():
                return jsonify({"msg": "Email already registered"}), 409
            user.email = new_email

    # Password update
    if 'new_password' in data:
        current_pw = data.get('current_password', '')
        if not check_password_hash(user.password_hash, current_pw):
            return jsonify({"msg": "Current password is incorrect"}), 400
        if len(data['new_password']) < 6:
            return jsonify({"msg": "New password must be at least 6 characters"}), 400
        user.password_hash = generate_password_hash(data['new_password'])

    db.session.commit()
    return jsonify({
        "msg": "Profile updated successfully",
        "user": user.to_dict()
    }), 200
