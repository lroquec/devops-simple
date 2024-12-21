"""
Route handlers for authentication endpoints
"""

from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from app.models import User
from app import db

# Create blueprint
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user

    Returns:
        tuple: JSON response and status code
    """
    data = request.get_json()

    # Validate input
    if not all(k in data for k in ("username", "password", "email")):
        return jsonify({"error": "Missing required fields"}), 400

    # Check if user exists
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already exists"}), 409

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 409

    # Create new user with role if provided
    user = User(
        username=data["username"],
        password=generate_password_hash(data["password"]),
        email=data["email"],
        role=data.get("role", "user"),  # Default to 'user' if not specified
    )

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return (
        jsonify(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user.to_dict(),
            }
        ),
        201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login user

    Returns:
        tuple: JSON response and status code
    """
    data = request.get_json()

    if not all(k in data for k in ("username", "password")):
        return jsonify({"error": "Missing username or password"}), 400

    user = User.query.filter_by(username=data["username"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Invalid username or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return (
        jsonify(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user.to_dict(),
            }
        ),
        200,
    )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token

    Returns:
        tuple: JSON response and status code
    """
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    return jsonify({"access_token": access_token}), 200


@auth_bp.route("/verify", methods=["GET"])
@jwt_required()
def verify():
    """Verify token and return user info

    Returns:
        tuple: JSON response and status code
    """
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(int(current_user_id))
    return jsonify({"user": user.to_dict()}), 200
