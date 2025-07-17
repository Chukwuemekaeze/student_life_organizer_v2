from flask import Blueprint, request, jsonify
from app.models.user import db, User
from flask_jwt_extended import create_access_token
import datetime

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"msg": "Email already exists"}), 400

    new_user = User(email=data["email"])
    new_user.set_password(data["password"])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "User registered"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data["email"]).first()
    if user and user.check_password(data["password"]):
        expires = datetime.timedelta(days=1)
        token = create_access_token(identity=user.id, expires_delta=expires)
        return jsonify(access_token=token)
    return jsonify({"msg": "Invalid credentials"}), 401
