import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from services.user_service import UserService
from database.base import get_db_connection
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Signup Route
@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    role = "user"

    db = next(get_db_connection())
    user_service = UserService(db)

    # Check if user already exists
    existing_user = user_service.get_user_by_username(username)
    if existing_user:
        return jsonify({"error": "Username already exists"}), 400

    hashed_password = generate_password_hash(password)

    user_data = {
        "username": username,
        "password_hash": hashed_password,
        "email": email,
        "role": role
    }

    created_user = user_service.create_user(user_data)

    if not created_user:
        return jsonify({"error": "User registration failed"}), 500

    return jsonify({
        "message": "User registered successfully",
        "user_id": created_user.id
    }), 201


# Login Route
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    db = next(get_db_connection())
    user_service = UserService(db)

    user = user_service.get_user_by_username(username)

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid username or password"}), 401

    token_payload = {
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    }

    token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")

    return jsonify({
        "access_token": token,
        "user": {
            "user_id": user.id,
            "username": user.username,
            "role": user.role
        }
    }), 200
