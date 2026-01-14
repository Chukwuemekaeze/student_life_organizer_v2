# app/agent/context.py
from __future__ import annotations
from typing import Dict, Any
from datetime import datetime, timezone
from app.utils.timezone import utcnow
from app.models.journal import JournalEntry
from app.models.task import Task
from app.models.notification import Notification

# Build a compact Context Pack (small, structured; not raw dumps)

def build_context_pack(user_id: int, include_recent_actions: bool = True) -> Dict[str, Any]:
    # Current date/time context
    now = utcnow()
    current_time = {
        "current_datetime": now.isoformat(),
        "current_date": now.date().isoformat(),
        "current_time": now.time().replace(microsecond=0).isoformat(),
        "timezone": "UTC",
        "day_of_week": now.strftime("%A"),
        "month": now.strftime("%B"),
        "year": now.year
    }
    # Recent journals
    journals = JournalEntry.query.filter_by(user_id=user_id).order_by(JournalEntry.timestamp.desc()).limit(5).all()
    j_pack = [{"id": j.id, "preview": (j.content or "")[:300], "created_at": j.timestamp.isoformat()} for j in journals]

    # Tasks snapshot
    todos = Task.query.filter_by(user_id=user_id, status="todo").order_by(Task.due_at.is_(None), Task.due_at.asc()).limit(10).all()
    done_recent = Task.query.filter_by(user_id=user_id, status="done").order_by(Task.completed_at.desc()).limit(5).all()
    t_pack = {
        "todo": [{"id": t.id, "title": t.title, "due_at": t.due_at.isoformat() if t.due_at else None, "priority": t.priority} for t in todos],
        "done_recent": [{"id": t.id, "title": t.title, "completed_at": t.completed_at.isoformat() if t.completed_at else None} for t in done_recent],
    }

    # Unread notifications
    notifs = Notification.query.filter_by(user_id=user_id).filter(Notification.read_at == None).order_by(Notification.created_at.desc()).limit(10).all()  # noqa: E711
    n_pack = [{"id": n.id, "kind": n.kind, "title": n.title} for n in notifs]

    return {
        "current_time": current_time,
        "journals": j_pack, 
        "tasks": t_pack, 
        "notifications": n_pack
    }

