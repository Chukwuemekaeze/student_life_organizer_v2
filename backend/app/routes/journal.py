# backend/app/routes/journal.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.journal import JournalEntry

journal_bp = Blueprint("journal", __name__, url_prefix="/api")

@journal_bp.route("/journal", methods=["POST"])
@jwt_required()
def create_journal():
    data = request.get_json() or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"msg": "Content required"}), 400

    entry = JournalEntry(content=content, user_id=get_jwt_identity())
    db.session.add(entry)
    db.session.commit()
    return jsonify({"id": entry.id, "msg": "created"}), 201
