from app.models import Course, Problem, ProblemLaunch, Submission, User


def get_dashboard_summary():
    return {
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
