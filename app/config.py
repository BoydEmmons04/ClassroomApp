import os

from sqlalchemy.engine import URL


def _database_url_from_env():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    if not os.getenv("POSTGRES_DB"):
        return None

    return URL.create(
        "postgresql+psycopg2",
        username=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST", "db"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=os.getenv("POSTGRES_DB"),
    )


class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    REQUEST_ID_HEADER = "X-Request-ID"

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = (
        _database_url_from_env() or "sqlite:///classroom_app_dev.sqlite3"
    )


class TestingConfig(BaseConfig):
    TESTING = True
    SECRET_KEY = os.getenv("SECRET_KEY", "test-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    @staticmethod
    def init_app(app):
        missing = [
            name
            for name in ("SECRET_KEY",)
            if not os.getenv(name)
        ]
        database_url = _database_url_from_env()
        if not database_url:
            missing.append("DATABASE_URL or POSTGRES_* database settings")

        if missing:
            raise RuntimeError(
                "Missing required production configuration: " + ", ".join(missing)
            )

        app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url


CONFIG_BY_NAME = {
    "development": DevelopmentConfig,
    "dev": DevelopmentConfig,
    "testing": TestingConfig,
    "test": TestingConfig,
    "production": ProductionConfig,
    "prod": ProductionConfig,
}


def get_config(config_name=None):
    name = config_name or os.getenv("APP_ENV") or os.getenv("FLASK_ENV") or "development"
    return CONFIG_BY_NAME.get(name.lower(), DevelopmentConfig)
