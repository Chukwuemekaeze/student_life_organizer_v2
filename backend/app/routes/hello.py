from flask import Blueprint, jsonify

hello_bp = Blueprint("hello", __name__)

@hello_bp.route("/api/hello")
def hello():
    return jsonify(message="Welcome to the Student Life Organiser backend!")
