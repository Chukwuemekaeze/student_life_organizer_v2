# backend/app/models/oauth_token.py
from datetime import datetime, timezone
from app.extensions import db

def utcnow():
    return datetime.now(timezone.utc)

class OAuthToken(db.Model):
    __tablename__ = "oauth_token"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    provider = db.Column(db.String(50), nullable=False, index=True)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=True)
    expiry = db.Column(db.DateTime(timezone=True), nullable=True)
    scopes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'provider', name='uq_oauth_token_user_provider'),
    )

    @classmethod
    def get_for_user(cls, user_id, provider):
        """Get the first matching token for a user and provider."""
        return cls.query.filter_by(user_id=user_id, provider=provider).first()
