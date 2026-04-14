from flask import jsonify

from app.models import Course, Problem, ProblemLaunch, Submission, User


def register_routes(app):
    """Register MVP smoke-test routes while full Jinja views are built out."""

    @app.get("/")
    def index():
        """Show app status plus plan-aligned database counts."""
        return jsonify(
            {
                "app": "Classroom Programming Challenge Platform",
                "status": "running",
                "counts": {
                    "users": User.query.count(),
                    "courses": Course.query.count(),
                    "problems": Problem.query.count(),
                    "launches": ProblemLaunch.query.count(),
                    "submissions": Submission.query.count(),
                },
                "recent_problems": [
                    {
                        "id": problem.id,
                        "title": problem.title,
                        "difficulty": problem.difficulty,
                        "language": problem.language,
                    }
                    for problem in Problem.query.order_by(Problem.id.desc()).limit(5)
                ],
            }
        )

    @app.get("/health")
    def health():
        """Health endpoint for quick container checks."""
        return jsonify({"status": "ok"})
