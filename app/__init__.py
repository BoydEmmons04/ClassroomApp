from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.config import get_config

# Shared extension instances live at module scope so models can import them
# without creating circular imports.
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_object=None):
    """Create and configure the Flask application for Docker and local runs."""
    app = Flask(__name__)
    config = config_object or get_config()
    app.config.from_object(config)
    config.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models after db is initialized so Flask-Migrate can discover them.
    from app import models  # noqa: F401

    from app.logging import register_request_logging
    from app.routes import register_routes

    register_request_logging(app)
    register_routes(app)

    return app
