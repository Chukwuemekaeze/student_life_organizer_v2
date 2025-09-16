# backend/app/models/__init__.py
# Import models so they register with SQLAlchemy
from .user import User        # noqa: F401
from .journal import JournalEntry  # noqa: F401
from .chat import ChatThread, ChatMessage  # noqa: F401
from .notion import NotionLink, NotionNoteCache  # noqa: F401
from .usage_log import UsageLog  # noqa: F401
from .task import Task  # noqa: F401
from .notification import Notification  # noqa: F401
