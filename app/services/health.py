from sqlalchemy import text

from app import db


def database_is_ready():
    try:
        db.session.execute(text("SELECT 1"))
    except Exception as exc:
        db.session.rollback()
        return {"ok": False, "error": exc.__class__.__name__}

    return {"ok": True}
