# backend/app/models/__init__.py
# Import models so they register with SQLAlchemy
from .user import User        # noqa: F401
from .journal import JournalEntry  # noqa: F401
