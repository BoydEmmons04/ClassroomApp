def register_routes(app):
    """Register application blueprints."""
    from app.blueprints.health.routes import health_bp
    from app.blueprints.main.routes import main_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(main_bp)
