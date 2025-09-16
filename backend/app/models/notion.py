from datetime import datetime
from app.extensions import db

class NotionLink(db.Model):
    __tablename__ = "notion_links"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    access_token = db.Column(db.String(255), nullable=False)
    workspace_name = db.Column(db.String(255))
    workspace_icon = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NotionNoteCache(db.Model):
    __tablename__ = "notion_note_cache"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True, nullable=False)
    page_id = db.Column(db.String(64), unique=True, nullable=False)
    title = db.Column(db.String(512))
    url = db.Column(db.String(512))
    last_edited_time = db.Column(db.DateTime, index=True)


