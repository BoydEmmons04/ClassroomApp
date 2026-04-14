from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Course, CourseEnrollment, User


def test_user_role_constraint_rejects_unknown_role(app):
    with app.app_context():
        db.session.add(
            User(
                name="Casey Example",
                email="casey@example.com",
                role="wizard",
            )
        )

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        else:
            raise AssertionError("invalid user role should violate database constraint")


def test_course_enrollment_is_unique_per_course_and_student(app):
    with app.app_context():
        professor = User(
            name="Professor Ada",
            email="ada@example.com",
            role="professor",
        )
        student = User(
            name="Student Grace",
            email="grace@example.com",
            role="student",
        )
        course = Course(course_name="Intro Programming", professor=professor)
        db.session.add_all([professor, student, course])
        db.session.commit()

        db.session.add(CourseEnrollment(course=course, student=student))
        db.session.commit()

        db.session.add(CourseEnrollment(course=course, student=student))

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        else:
            raise AssertionError("duplicate course enrollment should be rejected")
