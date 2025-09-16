from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.notification import Notification
from app.services.notify import scan_user_tasks_for_reminders

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")


@notifications_bp.route("/scan-due", methods=["POST","GET"])  # allow GET for easy Postman
@jwt_required()
def scan_due():
    uid = get_jwt_identity()
    soon_h = int(request.args.get("soon_hours", 24))
    over_d = int(request.args.get("overdue_days", 7))
    out = scan_user_tasks_for_reminders(uid, window_soon_hours=soon_h, overdue_window_days=over_d)
    return out, 200


@notifications_bp.route("/unread", methods=["GET"])  # unread for user
@jwt_required()
def unread():
    uid = get_jwt_identity()
    items = Notification.query.filter_by(user_id=uid).filter(Notification.read_at == None).order_by(Notification.created_at.desc()).limit(50).all()  # noqa: E711
    return {"items": [n.to_dict() for n in items], "count": len(items)}, 200


@notifications_bp.route("/mark-read", methods=["POST"])  # mark one or many
@jwt_required()
def mark_read():
    uid = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    ids = data.get("ids") or []
    now = datetime.utcnow()
    q = Notification.query.filter(Notification.user_id == uid, Notification.id.in_(ids))
    updated = 0
    for n in q.all():
        if n.read_at is None:
            n.read_at = now
            updated += 1
    db.session.commit()
    return {"updated": updated}, 200


@notifications_bp.route("/all", methods=["GET"])  # paginated history
@jwt_required()
def list_all():
    uid = get_jwt_identity()
    page = max(1, int(request.args.get("page", 1)))
    page_size = min(100, max(1, int(request.args.get("page_size", 20))))
    q = Notification.query.filter_by(user_id=uid).order_by(Notification.created_at.desc())
    items = q.paginate(page=page, per_page=page_size, error_out=False)
    return {
        "items": [n.to_dict() for n in items.items],
        "page": page,
        "page_size": page_size,
        "total": items.total,
        "pages": items.pages,
    }, 200
