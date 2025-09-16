from datetime import datetime
from app.extensions import db

class Notification(db.Model):
    __tablename__ = "notification"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True, nullable=False)

    kind = db.Column(db.String(50), nullable=False)  # e.g., task_due_soon, task_overdue
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text)

    ref_type = db.Column(db.String(50))  # e.g., task
    ref_id = db.Column(db.Integer)

    unique_key = db.Column(db.String(200), index=True)  # for de‑duplication

    scheduled_for = db.Column(db.DateTime, index=True)  # when it should appear
    delivered_at = db.Column(db.DateTime, index=True)   # when actually created/delivered

    read_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "kind": self.kind,
            "title": self.title,
            "body": self.body or "",
            "ref_type": self.ref_type,
            "ref_id": self.ref_id,
            "unique_key": self.unique_key,
            "scheduled_for": self.scheduled_for.isoformat() if self.scheduled_for else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
