from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional

from app.extensions import db
from app.models.notification import Notification
from app.models.task import Task

# De‑dup helper

def _exists_by_key(user_id: int, unique_key: str) -> bool:
    return db.session.query(Notification.id).filter_by(user_id=user_id, unique_key=unique_key).first() is not None


def create_notification(*, user_id: int, kind: str, title: str, body: str = "", ref_type: str | None = None, ref_id: int | None = None, unique_key: str | None = None, scheduled_for: datetime | None = None) -> Notification:
    if unique_key and _exists_by_key(user_id, unique_key):
        # already created
        return db.session.query(Notification).filter_by(user_id=user_id, unique_key=unique_key).first()
    n = Notification(
        user_id=user_id,
        kind=kind,
        title=title,
        body=body or "",
        ref_type=ref_type,
        ref_id=ref_id,
        unique_key=unique_key,
        scheduled_for=scheduled_for or datetime.utcnow(),
        delivered_at=datetime.utcnow(),
    )
    db.session.add(n)
    db.session.commit()
    return n


# === Scanners ===
# Create reminders for tasks due soon and overdue (no duplicates);
# window_soon: next N hours; overdue_window: past N days.

def scan_user_tasks_for_reminders(user_id: int, *, window_soon_hours: int = 24, overdue_window_days: int = 7) -> dict:
    now = datetime.utcnow()
    soon_after = now + timedelta(hours=window_soon_hours)
    overdue_after = now - timedelta(days=overdue_window_days)

    # Due soon (due_at within (now, soon]) and not done
    due_soon = (
        db.session.query(Task)
        .filter(Task.user_id == user_id, Task.status != "done", Task.due_at != None, Task.due_at > now, Task.due_at <= soon_after)  # noqa: E711
        .all()
    )
    # Overdue (due_at < now, not done, not too far in the past)
    overdue = (
        db.session.query(Task)
        .filter(Task.user_id == user_id, Task.status != "done", Task.due_at != None, Task.due_at < now, Task.due_at >= overdue_after)  # noqa: E711
        .all()
    )

    created = 0
    for t in due_soon:
        key = f"task_due_soon:{t.id}:{t.due_at.date().isoformat()}"
        title = f"Due soon: {t.title}"
        body = f"This task is due by {t.due_at.isoformat()} (priority: {t.priority})."
        if not _exists_by_key(user_id, key):
            create_notification(user_id=user_id, kind="task_due_soon", title=title, body=body, ref_type="task", ref_id=t.id, unique_key=key, scheduled_for=t.due_at)
            created += 1

    for t in overdue:
        key = f"task_overdue:{t.id}:{now.date().isoformat()}"  # one per day max
        title = f"Overdue: {t.title}"
        body = f"This task was due at {t.due_at.isoformat()} (priority: {t.priority})."
        if not _exists_by_key(user_id, key):
            create_notification(user_id=user_id, kind="task_overdue", title=title, body=body, ref_type="task", ref_id=t.id, unique_key=key, scheduled_for=t.due_at)
            created += 1

    return {"created": created, "due_soon": len(due_soon), "overdue": len(overdue)}
