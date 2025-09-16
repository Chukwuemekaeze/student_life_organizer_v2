from datetime import datetime
from app.extensions import db

class UsageLog(db.Model):
    __tablename__ = "usage_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True, nullable=False)
    event_type = db.Column(db.String(64), index=True, nullable=False)
    event_metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True, nullable=False)

    def __repr__(self):
        return f"<UsageLog {self.user_id} {self.event_type} {self.created_at}>"
