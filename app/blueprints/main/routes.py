from flask import Blueprint, jsonify

from app.services.dashboard import get_dashboard_summary

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    """Show app status plus plan-aligned database counts."""
    return jsonify(get_dashboard_summary())
