from datetime import datetime
from app.extensions import db

class Task(db.Model):
    __tablename__ = "task"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True, nullable=False)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    status = db.Column(db.String(20), default="todo", nullable=False)  # todo | in_progress | done
    priority = db.Column(db.String(20), default="medium", nullable=False)  # low | medium | high

    due_at = db.Column(db.DateTime, index=True)
    completed_at = db.Column(db.DateTime)

    source = db.Column(db.String(50), default="manual", nullable=False)  # manual | journal_extract | chat_quickadd | notion
    outlook_event_id = db.Column(db.String(128))  # reserved for Phase B (optional)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description or "",
            "status": self.status,
            "priority": self.priority,
            "due_at": self.due_at.isoformat() if self.due_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "source": self.source,
            "outlook_event_id": self.outlook_event_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

