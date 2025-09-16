from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_

from app.extensions import db
from app.models.task import Task
from app.services.metrics import log_event  # Phase 1 helper
from app.services.outlook_tasks import ensure_task_event, delete_task_event
from app.services.task_nlp import quick_extract_task


tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")

VALID_STATUS = {"todo", "in_progress", "done"}
VALID_PRIORITY = {"low", "medium", "high"}


def _parse_dt(val):
    if not val:
        return None
    try:
        # Accept ISO 8601: "2025-09-20T16:00:00Z" or "2025-09-20T16:00:00"
        v = str(val).replace("Z", "+00:00")
        return datetime.fromisoformat(v)
    except Exception:
        return None


def _validate_payload(data, partial=False):
    errors = {}
    if not partial:
        if not data.get("title") or not str(data.get("title")).strip():
            errors["title"] = "Title is required"
    if "status" in data and data["status"] not in VALID_STATUS:
        errors["status"] = f"Invalid status; expected one of {sorted(VALID_STATUS)}"
    if "priority" in data and data["priority"] not in VALID_PRIORITY:
        errors["priority"] = f"Invalid priority; expected one of {sorted(VALID_PRIORITY)}"
    if errors:
        return False, errors
    return True, None


@tasks_bp.route("", methods=["POST"])  # Create
@jwt_required()
def create_task():
    uid = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    ok, errs = _validate_payload(data)
    if not ok:
        return {"errors": errs}, 400

    t = Task(
        user_id=uid,
        title=data["title"].strip(),
        description=(data.get("description") or "").strip() or None,
        status=data.get("status", "todo"),
        priority=data.get("priority", "medium"),
        due_at=_parse_dt(data.get("due_at")),
        source=(data.get("source") or "manual"),
    )
    db.session.add(t)
    db.session.commit()

    try:
        log_event("task_create", {"id": t.id, "priority": t.priority})
    except Exception:
        pass

    # Outlook sync
    try:
        if t.due_at:
            eid = ensure_task_event(uid, t)
            if eid and eid != t.outlook_event_id:
                t.outlook_event_id = eid
                db.session.commit()
    except Exception:
        pass

    return jsonify(t.to_dict()), 201


@tasks_bp.route("", methods=["GET"])  # List with filters
@jwt_required()
def list_tasks():
    uid = get_jwt_identity()
    status = request.args.get("status")
    q = request.args.get("q")
    due_before = _parse_dt(request.args.get("due_before"))
    due_after = _parse_dt(request.args.get("due_after"))

    page = max(1, int(request.args.get("page", 1)))
    page_size = min(100, max(1, int(request.args.get("page_size", 20))))

    query = Task.query.filter_by(user_id=uid)
    if status in VALID_STATUS:
        query = query.filter(Task.status == status)
    if due_before:
        query = query.filter(Task.due_at != None, Task.due_at <= due_before)  # noqa: E711
    if due_after:
        query = query.filter(Task.due_at != None, Task.due_at >= due_after)  # noqa: E711
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Task.title.ilike(like), Task.description.ilike(like)))

    query = query.order_by(Task.due_at.is_(None), Task.due_at.asc(), Task.created_at.desc())

    items = query.paginate(page=page, per_page=page_size, error_out=False)
    return jsonify({
        "items": [t.to_dict() for t in items.items],
        "page": page,
        "page_size": page_size,
        "total": items.total,
        "pages": items.pages,
    })


@tasks_bp.route("/<int:task_id>", methods=["GET"])  # Get one
@jwt_required()
def get_task(task_id: int):
    uid = get_jwt_identity()
    t = Task.query.filter_by(id=task_id, user_id=uid).first()
    if not t:
        return {"msg": "Not found"}, 404
    return jsonify(t.to_dict())


@tasks_bp.route("/<int:task_id>", methods=["PATCH"])  # Update / complete
@jwt_required()
def update_task(task_id: int):
    uid = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    t = Task.query.filter_by(id=task_id, user_id=uid).first()
    if not t:
        return {"msg": "Not found"}, 404

    ok, errs = _validate_payload(data, partial=True)
    if not ok:
        return {"errors": errs}, 400

    # Apply changes
    if "title" in data and str(data["title"]).strip():
        t.title = data["title"].strip()
    if "description" in data:
        t.description = (data.get("description") or "").strip() or None
    if "priority" in data and data["priority"] in VALID_PRIORITY:
        t.priority = data["priority"]
    if "status" in data and data["status"] in VALID_STATUS:
        prev = t.status
        t.status = data["status"]
        if prev != "done" and t.status == "done":
            t.completed_at = datetime.utcnow()
            try:
                log_event("task_complete", {"id": t.id})
            except Exception:
                pass
    if "due_at" in data:
        t.due_at = _parse_dt(data.get("due_at"))

    db.session.commit()

    try:
        if t.due_at:
            eid = ensure_task_event(uid, t)
            if eid and eid != t.outlook_event_id:
                t.outlook_event_id = eid
                db.session.commit()
        else:
            delete_task_event(uid, t)
            if t.outlook_event_id:
                t.outlook_event_id = None
                db.session.commit()
    except Exception:
        pass

    if data.keys() - {"status"}:
        try:
            log_event("task_update", {"id": t.id})
        except Exception:
            pass

    return jsonify(t.to_dict())


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])  # Delete (hard delete for MVP)
@jwt_required()
def delete_task(task_id: int):
    uid = get_jwt_identity()
    t = Task.query.filter_by(id=task_id, user_id=uid).first()
    if not t:
        return {"msg": "Not found"}, 404

    try:
        delete_task_event(uid, t)
    except Exception:
        pass

    db.session.delete(t)
    db.session.commit()

    try:
        log_event("task_delete", {"id": task_id})
    except Exception:
        pass

    return {"msg": "deleted"}, 200


@tasks_bp.route("/quickadd", methods=["POST"])
@jwt_required()
def quickadd():
    uid = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return {"msg": "text required"}, 400
    try:
        cand = quick_extract_task(text)
    except Exception as e:
        return {"msg": f"nlp_error: {e}"}, 502

    t = Task(
        user_id=uid,
        title=cand["title"],
        description=data.get("description"),
        priority=cand["priority"],
        status="todo",
        due_at=_parse_dt(cand.get("due_at")),
        source="chat_quickadd",
    )
    db.session.add(t)
    db.session.commit()

    try:
        log_event("task_create", {"id": t.id, "priority": t.priority, "source": "chat_quickadd"})
    except Exception:
        pass

    # Sync to Outlook if due_at exists
    try:
        if t.due_at:
            eid = ensure_task_event(uid, t)
            if eid and eid != t.outlook_event_id:
                t.outlook_event_id = eid
                db.session.commit()
    except Exception:
        pass

    return t.to_dict(), 201

