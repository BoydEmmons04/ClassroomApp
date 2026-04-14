"""harden schema for operations

Revision ID: 2a7c9d4e1b30
Revises: 8b2d2f5c7a10
Create Date: 2026-04-14 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2a7c9d4e1b30"
down_revision = "8b2d2f5c7a10"
branch_labels = None
depends_on = None


TIMESTAMP_COLUMNS = (
    ("users", "created_at"),
    ("courses", "created_at"),
    ("course_enrollments", "joined_at"),
    ("problems", "created_at"),
    ("problem_launches", "start_time"),
    ("submissions", "submitted_at"),
    ("attendance", "recorded_at"),
    ("problem_submissions_for_approval", "submitted_at"),
)

NULLABLE_TIMESTAMP_COLUMNS = (
    ("problem_launches", "end_time"),
    ("problem_submissions_for_approval", "reviewed_at"),
)


INDEXES = (
    ("ix_users_role", "users", ["role"]),
    ("ix_users_created_at", "users", ["created_at"]),
    ("ix_courses_professor_id", "courses", ["professor_id"]),
    ("ix_courses_created_at", "courses", ["created_at"]),
    ("ix_course_enrollments_course_id", "course_enrollments", ["course_id"]),
    ("ix_course_enrollments_student_id", "course_enrollments", ["student_id"]),
    ("ix_course_enrollments_joined_at", "course_enrollments", ["joined_at"]),
    ("ix_problems_title", "problems", ["title"]),
    ("ix_problems_problem_type", "problems", ["problem_type"]),
    ("ix_problems_language", "problems", ["language"]),
    ("ix_problems_difficulty", "problems", ["difficulty"]),
    ("ix_problems_approval_status", "problems", ["approval_status"]),
    ("ix_problems_created_by", "problems", ["created_by"]),
    ("ix_problems_created_at", "problems", ["created_at"]),
    ("ix_problem_launches_problem_id", "problem_launches", ["problem_id"]),
    ("ix_problem_launches_course_id", "problem_launches", ["course_id"]),
    (
        "ix_problem_launches_launched_by_professor_id",
        "problem_launches",
        ["launched_by_professor_id"],
    ),
    ("ix_problem_launches_start_time", "problem_launches", ["start_time"]),
    ("ix_problem_launches_end_time", "problem_launches", ["end_time"]),
    ("ix_problem_launches_status", "problem_launches", ["status"]),
    ("ix_submissions_launch_id", "submissions", ["launch_id"]),
    ("ix_submissions_student_id", "submissions", ["student_id"]),
    ("ix_submissions_submitted_at", "submissions", ["submitted_at"]),
    ("ix_attendance_launch_id", "attendance", ["launch_id"]),
    ("ix_attendance_student_id", "attendance", ["student_id"]),
    ("ix_attendance_recorded_at", "attendance", ["recorded_at"]),
    (
        "ix_problem_submissions_for_approval_problem_id",
        "problem_submissions_for_approval",
        ["problem_id"],
    ),
    (
        "ix_problem_submissions_for_approval_submitted_by_professor_id",
        "problem_submissions_for_approval",
        ["submitted_by_professor_id"],
    ),
    (
        "ix_problem_submissions_for_approval_review_status",
        "problem_submissions_for_approval",
        ["review_status"],
    ),
    (
        "ix_problem_submissions_for_approval_reviewer_id",
        "problem_submissions_for_approval",
        ["reviewer_id"],
    ),
    (
        "ix_problem_submissions_for_approval_submitted_at",
        "problem_submissions_for_approval",
        ["submitted_at"],
    ),
    (
        "ix_problem_submissions_for_approval_reviewed_at",
        "problem_submissions_for_approval",
        ["reviewed_at"],
    ),
)


def upgrade():
    for table_name, column_name in TIMESTAMP_COLUMNS:
        op.alter_column(
            table_name,
            column_name,
            existing_type=sa.DateTime(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )

    for table_name, column_name in NULLABLE_TIMESTAMP_COLUMNS:
        op.alter_column(
            table_name,
            column_name,
            existing_type=sa.DateTime(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=True,
        )

    op.create_check_constraint(
        "ck_users_role",
        "users",
        "role in ('student', 'professor', 'admin')",
    )
    op.create_check_constraint(
        "ck_problems_difficulty",
        "problems",
        "difficulty in ('easy', 'medium', 'hard')",
    )
    op.create_check_constraint(
        "ck_problems_approval_status",
        "problems",
        "approval_status in ('pending', 'approved', 'rejected')",
    )
    op.create_check_constraint(
        "ck_problem_launches_status",
        "problem_launches",
        "status in ('active', 'closed', 'archived')",
    )
    op.create_check_constraint(
        "ck_problem_launches_time_order",
        "problem_launches",
        "end_time > start_time",
    )
    op.create_check_constraint(
        "ck_problem_submissions_review_status",
        "problem_submissions_for_approval",
        "review_status in ('pending', 'approved', 'rejected')",
    )
    op.create_unique_constraint(
        "uq_attendance_launch_student",
        "attendance",
        ["launch_id", "student_id"],
    )

    for index_name, table_name, columns in INDEXES:
        op.create_index(index_name, table_name, columns, unique=False)


def downgrade():
    for index_name, table_name, _columns in reversed(INDEXES):
        op.drop_index(index_name, table_name=table_name)

    op.drop_constraint("uq_attendance_launch_student", "attendance", type_="unique")
    op.drop_constraint(
        "ck_problem_submissions_review_status",
        "problem_submissions_for_approval",
        type_="check",
    )
    op.drop_constraint(
        "ck_problem_launches_time_order",
        "problem_launches",
        type_="check",
    )
    op.drop_constraint(
        "ck_problem_launches_status",
        "problem_launches",
        type_="check",
    )
    op.drop_constraint(
        "ck_problems_approval_status",
        "problems",
        type_="check",
    )
    op.drop_constraint("ck_problems_difficulty", "problems", type_="check")
    op.drop_constraint("ck_users_role", "users", type_="check")

    for table_name, column_name in TIMESTAMP_COLUMNS:
        op.alter_column(
            table_name,
            column_name,
            existing_type=sa.DateTime(timezone=True),
            type_=sa.DateTime(),
            existing_nullable=False,
            server_default=None,
        )

    for table_name, column_name in NULLABLE_TIMESTAMP_COLUMNS:
        op.alter_column(
            table_name,
            column_name,
            existing_type=sa.DateTime(timezone=True),
            type_=sa.DateTime(),
            existing_nullable=True,
        )
