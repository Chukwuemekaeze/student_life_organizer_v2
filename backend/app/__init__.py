# backend/app/__init__.py
from flask import Flask, request
from flask_cors import CORS
from dotenv import load_dotenv
import os

from app.extensions import db, migrate, jwt

def create_app():
    load_dotenv()

    app = Flask(__name__)

    # Config
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///slo.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Chat History Configuration
    app.config["CHAT_HISTORY_ENABLED"] = os.getenv("CHAT_HISTORY_ENABLED", "true").lower() == "true"
    app.config["CHAT_DEFAULT_RETENTION_DAYS"] = int(os.getenv("CHAT_DEFAULT_RETENTION_DAYS", "60"))
    app.config["CHAT_AUTOSAVE_DEFAULT"] = os.getenv("CHAT_AUTOSAVE_DEFAULT", "true").lower() == "true"

    # Init extensions
    CORS(app, 
         origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
         supports_credentials=True)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Import models so Alembic sees them
    from app.models import user, journal, oauth_token, chat, notion, usage_log  # noqa: F401

    # Register routes
    from app.routes.auth import auth_bp
    from app.routes.hello import hello_bp
    from app.routes.journal import journal_bp
    from app.routes.calendar import calendar_bp
    from app.routes.outlook_oauth import outlook_bp
    from app.routes.ai import ai_bp
    from app.routes.chat import chat_bp
    from app.routes.notes import notes_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.tasks import tasks_bp
    from app.routes.notifications import notifications_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(hello_bp)
    app.register_blueprint(journal_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(outlook_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(notifications_bp)

    # 🔎 log every incoming request **once**
    @app.before_request
    def trace():
        print(f">> {request.method} {request.path}")

    # app/__init__.py  inside create_app(), right before `return app`
    for rule in app.url_map.iter_rules():
        print("=>", rule)

    return app
