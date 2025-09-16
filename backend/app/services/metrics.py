from app.extensions import db
from app.models.usage_log import UsageLog

from flask_jwt_extended import get_jwt_identity

def log_event(event_type: str, metadata: dict | None = None):
    try:
        uid = get_jwt_identity()
    except Exception:
        uid = None
    if not uid:
        return
    log = UsageLog(user_id=uid, event_type=event_type, event_metadata=metadata or {})
    db.session.add(log)
    db.session.commit()
