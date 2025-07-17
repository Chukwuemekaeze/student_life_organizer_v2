# backend/app/__init__.py
from flask import Flask
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
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///slo.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Init extensions
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Import models so Alembic sees them
    from app.models import user, journal  # noqa: F401

    # Register routes
    from app.routes.auth import auth_bp
    from app.routes.hello import hello_bp
    from app.routes.journal import journal_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(hello_bp)
    app.register_blueprint(journal_bp)

    return app
