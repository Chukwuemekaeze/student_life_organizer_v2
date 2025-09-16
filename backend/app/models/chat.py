from datetime import datetime
from app.extensions import db

class ChatThread(db.Model):
    __tablename__ = 'chat_thread'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, nullable=False)
    title = db.Column(db.String(200), nullable=False, default='New chat')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    retention_days = db.Column(db.Integer)

class ChatMessage(db.Model):
    __tablename__ = 'chat_message'
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('chat_thread.id', ondelete='CASCADE'), index=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, nullable=False)
    role = db.Column(db.String(16), nullable=False)  # 'user' | 'assistant' | 'system'
    content = db.Column(db.Text, nullable=False)
    tools_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True, nullable=False)

