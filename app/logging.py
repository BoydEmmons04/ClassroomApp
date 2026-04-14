import logging
import time
from uuid import uuid4

from flask import g, request


def register_request_logging(app):
    """Attach request IDs and concise access logs to every request."""
    logging.basicConfig(
        level=app.config.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    @app.before_request
    def start_request_timer():
        header_name = app.config["REQUEST_ID_HEADER"]
        g.request_id = request.headers.get(header_name, str(uuid4()))
        g.request_started_at = time.perf_counter()

    @app.after_request
    def add_request_metadata(response):
        duration_ms = (time.perf_counter() - g.request_started_at) * 1000
        response.headers[app.config["REQUEST_ID_HEADER"]] = g.request_id

        app.logger.info(
            "request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
            g.request_id,
            request.method,
            request.path,
            response.status_code,
            duration_ms,
        )
        return response
