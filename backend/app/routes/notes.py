from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.notion import NotionLink, NotionNoteCache
from app.services.notion_client import NotionClient, NotionAuthError, NotionAPIError
from app.services.metrics import log_event
from datetime import datetime

notes_bp = Blueprint("notes", __name__, url_prefix="/api/notes")

@notes_bp.route("/status", methods=["GET"])
@jwt_required()
def status():
    uid = get_jwt_identity()
    link = NotionLink.query.filter_by(user_id=uid).first()
    return jsonify({
        "connected": bool(link),
        "workspace_name": link.workspace_name if link else None,
    }), 200

@notes_bp.route("/connect", methods=["POST"])
@jwt_required()
def connect():
    uid = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    token = data.get("token")
    if not token:
        return jsonify({"msg": "token required"}), 400
    try:
        client = NotionClient(token)
        meta = client.whoami()
    except NotionAuthError as e:
        return jsonify({"msg": str(e)}), 400
    except NotionAPIError:
        return jsonify({"msg": "Notion API error"}), 502
    link = NotionLink.query.filter_by(user_id=uid).first()
    if not link:
        link = NotionLink(user_id=uid, access_token=token)
        db.session.add(link)
    else:
        link.access_token = token
    link.workspace_name = meta.get("workspace_name")
    db.session.commit()
    return jsonify({"connected": True, "workspace_name": link.workspace_name}), 200

@notes_bp.route("/disconnect", methods=["DELETE"])
@jwt_required()
def disconnect():
    uid = get_jwt_identity()
    NotionLink.query.filter_by(user_id=uid).delete()
    NotionNoteCache.query.filter_by(user_id=uid).delete()
    db.session.commit()
    return jsonify({"connected": False}), 200

@notes_bp.route("/sync", methods=["POST"])
@jwt_required()
def sync_notes():
    uid = get_jwt_identity()
    link = NotionLink.query.filter_by(user_id=uid).first()
    if not link:
        return jsonify({"msg": "Not connected to Notion"}), 400
    try:
        client = NotionClient(link.access_token)
        items = client.list_recent_pages(limit=10)
    except NotionAuthError as e:
        return jsonify({"msg": str(e)}), 400
    except NotionAPIError:
        return jsonify({"msg": "Notion API error"}), 502
    # Upsert cache
    page_ids = set()
    for it in items:
        page_ids.add(it["page_id"])
        row = NotionNoteCache.query.filter_by(page_id=it["page_id"]).first()
        dt = None
        try:
            dt = datetime.fromisoformat(it["last_edited_time"].replace("Z", "+00:00")) if it["last_edited_time"] else None
        except Exception:
            dt = None
        if not row:
            row = NotionNoteCache(
                user_id=uid,
                page_id=it["page_id"],
                title=it["title"],
                url=it["url"],
                last_edited_time=dt,
            )
            db.session.add(row)
        else:
            row.title = it["title"]
            row.url = it["url"]
            row.last_edited_time = dt
    # prune extras (keep only newest 20 for safety)
    db.session.commit()
    # Log the notes sync event
    try:
        log_event("notes_sync", {"synced": len(items)})
    except Exception:
        pass  # Non-blocking, fail silently
    return jsonify({"synced": len(items)}), 200

@notes_bp.route("/list", methods=["GET"])
@jwt_required()
def list_notes():
    uid = get_jwt_identity()
    limit = min(max(int(request.args.get("limit", 10)), 1), 20)
    q = NotionNoteCache.query.filter_by(user_id=uid).order_by(NotionNoteCache.last_edited_time.desc())
    rows = q.limit(limit).all()
    data = [{
        "page_id": r.page_id,
        "title": r.title,
        "url": r.url,
        "last_edited_time": r.last_edited_time.isoformat() if r.last_edited_time else None,
    } for r in rows]
    return jsonify({"items": data}), 200
