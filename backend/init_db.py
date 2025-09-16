from main import create_app
from app.extensions import db
from app.models import User, JournalEntry, ChatThread, ChatMessage, NotionLink, NotionNoteCache, Notification

app = create_app()

with app.app_context():
    # Drop all tables
    db.drop_all()
    
    # Create all tables
    db.create_all()
    
    print("Database initialized successfully!")


