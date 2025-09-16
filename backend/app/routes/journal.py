# backend/app/routes/journal.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc
from app.extensions import db
from app.models.journal import JournalEntry
from app.services.metrics import log_event

journal_bp = Blueprint("journal", __name__, url_prefix="/api")

@journal_bp.route("/journal", methods=["GET"])
@jwt_required()
def get_journals():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    search_query = request.args.get("q", "").strip()

    # Base query for current user's entries
    query = JournalEntry.query.filter_by(user_id=get_jwt_identity())

    # Apply search if provided
    if search_query:
        query = query.filter(JournalEntry.content.ilike(f"%{search_query}%"))

    # Order by newest first and paginate
    paginated = query.order_by(desc(JournalEntry.timestamp)).paginate(
        page=page, per_page=limit, error_out=False
    )

    return jsonify({
        "entries": [entry.to_dict() for entry in paginated.items],
        "total": paginated.total,
        "page": page,
        "pages": paginated.pages
    })

@journal_bp.route("/journal/<int:id>", methods=["GET"])
@jwt_required()
def get_journal(id):
    entry = JournalEntry.query.filter_by(
        id=id, user_id=get_jwt_identity()
    ).first()
    
    if not entry:
        return jsonify({"msg": "Entry not found"}), 404
    
    return jsonify(entry.to_dict())

@journal_bp.route("/journal/<int:id>", methods=["PUT"])
@jwt_required()
def update_journal(id):
    entry = JournalEntry.query.filter_by(
        id=id, user_id=get_jwt_identity()
    ).first()
    
    if not entry:
        return jsonify({"msg": "Entry not found"}), 404

    data = request.get_json() or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"msg": "Content required"}), 400

    entry.content = content
    db.session.commit()
    
    return jsonify(entry.to_dict())

@journal_bp.route("/journal/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_journal(id):
    entry = JournalEntry.query.filter_by(
        id=id, user_id=get_jwt_identity()
    ).first()
    
    if not entry:
        return jsonify({"msg": "Entry not found"}), 404

    db.session.delete(entry)
    db.session.commit()
    
    return jsonify({"msg": "Deleted"})

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
    # Log the event
    try:
        log_event("journal_create", {"id": entry.id})
    except Exception:
        pass  # Non-blocking, fail silently
    return jsonify(entry.to_dict()), 201
