from flask import Blueprint, jsonify

from app.services.health import database_is_ready

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
@health_bp.get("/health/live")
def live():
    """Confirm the Flask process can serve requests."""
    return jsonify({"status": "ok"})


@health_bp.get("/health/ready")
def ready():
    """Confirm dependencies required to serve traffic are reachable."""
    database_status = database_is_ready()
    status_code = 200 if database_status["ok"] else 503

    return (
        jsonify(
            {
                "status": "ready" if database_status["ok"] else "not_ready",
                "checks": {"database": database_status},
            }
        ),
        status_code,
    )
