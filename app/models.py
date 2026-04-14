from datetime import datetime

from app import db


class User(db.Model):
    """Google-authenticated professor, student, or admin account."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    google_oauth_id = db.Column(db.String(255), unique=True, nullable=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    role = db.Column(db.String(30), nullable=False, default="student")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    taught_courses = db.relationship("Course", back_populates="professor")
    enrollments = db.relationship("CourseEnrollment", back_populates="student")
    created_problems = db.relationship("Problem", back_populates="creator")
    submissions = db.relationship("Submission", back_populates="student")


class Course(db.Model):
    """Professor-owned course or section that students can join."""

    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(160), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    term_or_semester = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    professor = db.relationship("User", back_populates="taught_courses")
    enrollments = db.relationship("CourseEnrollment", back_populates="course")
    launches = db.relationship("ProblemLaunch", back_populates="course")


class CourseEnrollment(db.Model):
    """Links a student account to a course roster."""

    __tablename__ = "course_enrollments"
    __table_args__ = (
        db.UniqueConstraint("course_id", "student_id", name="uq_course_student"),
    )

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    course = db.relationship("Course", back_populates="enrollments")
    student = db.relationship("User", back_populates="enrollments")


class Problem(db.Model):
    """Shared programming challenge that professors can search and launch."""

    __tablename__ = "problems"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.String(255), nullable=True)
    hint = db.Column(db.Text, nullable=True)
    problem_type = db.Column(db.String(80), nullable=False)
    language = db.Column(db.String(40), nullable=False, default="python")
    difficulty = db.Column(db.String(30), nullable=False, default="easy")
    starter_code = db.Column(db.Text, nullable=True)
    approval_status = db.Column(db.String(30), nullable=False, default="approved")
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    creator = db.relationship("User", back_populates="created_problems")
    launches = db.relationship("ProblemLaunch", back_populates="problem")


class ProblemLaunch(db.Model):
    """A professor's live launch of one problem to one course."""

    __tablename__ = "problem_launches"

    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey("problems.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    launched_by_professor_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="active")
    settings_json = db.Column(db.JSON, nullable=True)

    problem = db.relationship("Problem", back_populates="launches")
    course = db.relationship("Course", back_populates="launches")
    professor = db.relationship("User")
    submissions = db.relationship("Submission", back_populates="launch")
    attendance_records = db.relationship("Attendance", back_populates="launch")


class Submission(db.Model):
    """One-time student response shown anonymously in professor review views."""

    __tablename__ = "submissions"
    __table_args__ = (
        db.UniqueConstraint("launch_id", "student_id", name="uq_launch_student"),
    )

    id = db.Column(db.Integer, primary_key=True)
    launch_id = db.Column(
        db.Integer,
        db.ForeignKey("problem_launches.id"),
        nullable=False,
    )
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    student_display_name_for_attendance = db.Column(db.String(120), nullable=False)
    submitted_code = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    professor_review_label = db.Column(db.String(80), nullable=True)
    professor_notes = db.Column(db.Text, nullable=True)
    pinned_flag = db.Column(db.Boolean, default=False, nullable=False)
    archived_for_instruction_flag = db.Column(db.Boolean, default=False, nullable=False)

    launch = db.relationship("ProblemLaunch", back_populates="submissions")
    student = db.relationship("User", back_populates="submissions")


class Attendance(db.Model):
    """Separate participation record for roster tracking, not anonymous review."""

    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    launch_id = db.Column(
        db.Integer,
        db.ForeignKey("problem_launches.id"),
        nullable=False,
    )
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    attendance_name = db.Column(db.String(120), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    launch = db.relationship("ProblemLaunch", back_populates="attendance_records")
    student = db.relationship("User")


class ProblemSubmissionForApproval(db.Model):
    """Professor-submitted problem draft waiting for shared database approval."""

    __tablename__ = "problem_submissions_for_approval"

    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey("problems.id"), nullable=True)
    submitted_by_professor_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )
    review_status = db.Column(db.String(30), nullable=False, default="pending")
    reviewer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    problem = db.relationship("Problem")
    submitted_by_professor = db.relationship(
        "User",
        foreign_keys=[submitted_by_professor_id],
    )
    reviewer = db.relationship("User", foreign_keys=[reviewer_id])
