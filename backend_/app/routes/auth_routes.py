from flask import Blueprint, request, jsonify
from app.models.user import User
from app.db import db
from werkzeug.security import generate_password_hash, check_password_hash

auth_routes = Blueprint('auth_routes', __name__)

# Register User Route
@auth_routes.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password') or not data.get('username') or not data.get('name'):
        return jsonify({"error": "Missing required fields"}), 400

    # Hash password
    hashed_password = generate_password_hash(data['password'])  # No need to specify method

    new_user = User(email=data['email'], username=data['username'], password=hashed_password, name=data['name'])

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# Login User Route (Without JWT)
@auth_routes.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=data['email']).first()

    if user and check_password_hash(user.password, data['password']):
        return jsonify({"message": "Login successful", "user_id": user.id, "username": user.username}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401
