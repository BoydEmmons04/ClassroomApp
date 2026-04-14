import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import URL

# Shared extension instances live at module scope so models can import them
# without creating circular imports.
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    """Create and configure the Flask application for Docker and local runs."""
    app = Flask(__name__)

    # SECRET_KEY is required for sessions/forms; the fallback keeps dev builds
    # from crashing before a real secret is added to .env.
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only-change-me")

    # Prefer an explicit DATABASE_URL when one is supplied, otherwise build the
    # Postgres URL from Compose's POSTGRES_* values so special characters in the
    # password are escaped correctly.
    database_url = os.getenv("DATABASE_URL")
    if not database_url and os.getenv("POSTGRES_DB"):
        database_url = URL.create(
            "postgresql+psycopg2",
            username=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST", "db"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            database=os.getenv("POSTGRES_DB"),
        )

    # The sqlite fallback lets simple Flask commands run even when Postgres is
    # not started, which is useful during early project setup.
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        database_url or "sqlite:///classroom_app_dev.sqlite3"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models after db is initialized so Flask-Migrate can discover them.
    from app import models  # noqa: F401

    # Keep route definitions outside the app factory so the project can grow
    # into separate professor, student, course, and submission views.
    from app.routes import register_routes

    register_routes(app)

    return app
