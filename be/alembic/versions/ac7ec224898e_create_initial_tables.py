"""create initial tables

Revision ID: ac7ec224898e
Revises: 
Create Date: 2025-10-25 19:21:16.472962
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mssql import NVARCHAR, DATETIME2, UNIQUEIDENTIFIER as mssqlUUID

# revision identifiers, used by Alembic.
revision: str = 'ac7ec224898e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    # Tạo bảng users
    op.create_table(
        "users",
        sa.Column("user_id", mssqlUUID(), nullable=False, server_default=sa.text("NEWID()")),
        sa.Column("username", NVARCHAR(50), nullable=False),
        sa.Column("email", NVARCHAR(100), nullable=False),
        sa.Column("password", NVARCHAR(255), nullable=False),
        sa.Column("role", sa.Enum("child", "admin", name="role_enum"), nullable=False),
        sa.Column("name", NVARCHAR(100), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email")
    )

    # Tạo bảng children
    op.create_table(
        "children",
        sa.Column("user_id", mssqlUUID(), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("last_played", DATETIME2(), nullable=True),
        sa.Column("report_preferences", sa.Enum("daily", "weekly", "monthly", name="report_type_enum"), nullable=True),
        sa.Column("created_at", DATETIME2(), nullable=False),
        sa.Column("last_login", DATETIME2(), nullable=True),
        sa.PrimaryKeyConstraint("user_id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], name="fk_children_user_id")
    )

    # Tạo bảng games
    op.create_table(
        "games",
        sa.Column("game_id", mssqlUUID(), nullable=False, server_default=sa.text("NEWID()")),
        sa.Column("game_type", sa.Enum("GameClick", "GameCV", name="game_type_enum"), nullable=False),
        sa.Column("name", NVARCHAR(100), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("difficulty_level", sa.Integer(), nullable=False),
        sa.Column("max_errors", sa.Integer(), nullable=False, server_default=sa.text("3")),
        sa.Column("level_threshold", sa.Integer(), nullable=False),
        sa.Column("time_limit", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("game_id")
    )

    # Tạo bảng game_content
    op.create_table(
        "game_content",
        sa.Column("content_id", mssqlUUID(), nullable=False, server_default=sa.text("NEWID()")),
        sa.Column("game_id", mssqlUUID(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("content_type", sa.Enum("text", "image", "video", "audio", name="content_type_enum"), nullable=False),
        sa.Column("media_path", NVARCHAR(255), nullable=True),
        sa.Column("question_text", NVARCHAR(500), nullable=True),
        sa.Column("correct_answer", NVARCHAR(50), nullable=True),
        sa.Column("emotion", NVARCHAR(50), nullable=True),
        sa.Column("explanation", NVARCHAR(1000), nullable=True),
        sa.PrimaryKeyConstraint("content_id"),
        sa.ForeignKeyConstraint(["game_id"], ["games.game_id"], name="fk_game_content_game_id")
    )

    # Tạo bảng questions
    op.create_table(
        "questions",
        sa.Column("question_id", mssqlUUID(), nullable=False, server_default=sa.text("NEWID()")),
        sa.Column("game_id", mssqlUUID(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("content_id", mssqlUUID(), nullable=False),
        sa.Column("correct_answer", NVARCHAR(50), nullable=False),
        sa.PrimaryKeyConstraint("question_id"),
        sa.ForeignKeyConstraint(["game_id"], ["games.game_id"], name="fk_questions_game_id"),
        sa.ForeignKeyConstraint(["content_id"], ["game_content.content_id"], name="fk_questions_content_id")
    )

    # Tạo bảng question_answer_options (mối quan hệ nhiều-nhiều)
    op.create_table(
        "question_answer_options",
        sa.Column("question_id", mssqlUUID(), nullable=False),
        sa.Column("content_id", mssqlUUID(), nullable=False),
        sa.PrimaryKeyConstraint("question_id", "content_id"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.question_id"], name="fk_question_answer_options_question_id"),
        sa.ForeignKeyConstraint(["content_id"], ["game_content.content_id"], name="fk_question_answer_options_content_id")
    )

    # Tạo bảng game_data
    op.create_table(
        "game_data",
        sa.Column("data_id", mssqlUUID(), nullable=False, server_default=sa.text("NEWID()")),
        sa.Column("game_id", mssqlUUID(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("data_id"),
        sa.ForeignKeyConstraint(["game_id"], ["games.game_id"], name="fk_game_data_game_id")
    )

    # Tạo bảng game_data_contents (mối quan hệ nhiều-nhiều)
    op.create_table(
        "game_data_contents",
        sa.Column("data_id", mssqlUUID(), nullable=False),
        sa.Column("content_id", mssqlUUID(), nullable=False),
        sa.PrimaryKeyConstraint("data_id", "content_id"),
        sa.ForeignKeyConstraint(["data_id"], ["game_data.data_id"], name="fk_game_data_contents_data_id"),
        sa.ForeignKeyConstraint(["content_id"], ["game_content.content_id"], name="fk_game_data_contents_content_id")
    )

    # Tạo bảng emotion_concepts
    op.create_table(
        "emotion_concepts",
        sa.Column("concept_id", mssqlUUID(), nullable=False, server_default=sa.text("NEWID()")),
        sa.Column("emotion", NVARCHAR(50), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("title", NVARCHAR(100), nullable=False),
        sa.Column("video_path", NVARCHAR(255), nullable=True),
        sa.Column("image_path", NVARCHAR(255), nullable=True),
        sa.Column("audio_path", NVARCHAR(255), nullable=True),
        sa.Column("description", NVARCHAR(1000), nullable=True),
        sa.PrimaryKeyConstraint("concept_id")
    )

    # Tạo bảng sessions
    op.create_table(
        "sessions",
        sa.Column("session_id", mssqlUUID(), nullable=False, server_default=sa.text("NEWID()")),
        sa.Column("user_id", mssqlUUID(), nullable=False),
        sa.Column("game_id", mssqlUUID(), nullable=False),
        sa.Column("start_time", DATETIME2(), nullable=False),
        sa.Column("end_time", DATETIME2(), nullable=True),
        sa.Column("state", sa.Enum("playing", "pause", "end", name="session_state_enum"), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("emotion_errors", NVARCHAR(1000), nullable=False, server_default="{}"),
        sa.Column("max_errors", sa.Integer(), nullable=False),
        sa.Column("level_threshold", sa.Integer(), nullable=False),
        sa.Column("ratio", NVARCHAR(1000), nullable=False, server_default="[]"),
        sa.Column("time_limit", sa.Integer(), nullable=False),
        sa.Column("question_ids", NVARCHAR(1000), nullable=False, server_default="[]"),
        sa.PrimaryKeyConstraint("session_id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], name="fk_sessions_user_id"),
        sa.ForeignKeyConstraint(["game_id"], ["games.game_id"], name="fk_sessions_game_id")
    )

    # Tạo bảng session_questions
    op.create_table(
        "session_questions",
        sa.Column("id", mssqlUUID(), nullable=False, server_default=sa.text("NEWID()")),
        sa.Column("session_id", mssqlUUID(), nullable=False),
        sa.Column("question_id", mssqlUUID(), nullable=False),
        sa.Column("user_answer", NVARCHAR(255), nullable=True),
        sa.Column("correct_answer", NVARCHAR(255), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("response_time_ms", sa.Integer(), nullable=False),
        sa.Column("check_hint", sa.Boolean(), nullable=False),
        sa.Column("cv_confidence", sa.Float(), nullable=True),
        sa.Column("timestamp", DATETIME2(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.session_id"], name="fk_session_questions_session_id"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.question_id"], name="fk_session_questions_question_id")
    )

    # Tạo bảng session_history
    op.create_table(
        "session_history",
        sa.Column("session_history_id", mssqlUUID(), nullable=False, server_default=sa.text("NEWID()")),
        sa.Column("child_id", mssqlUUID(), nullable=False),
        sa.Column("game_id", mssqlUUID(), nullable=False),
        sa.Column("session_id", mssqlUUID(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("start_time", DATETIME2(), nullable=False),
        sa.Column("end_time", DATETIME2(), nullable=True),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("session_history_id"),
        sa.ForeignKeyConstraint(["child_id"], ["children.user_id"], name="fk_session_history_child_id"),
        sa.ForeignKeyConstraint(["game_id"], ["games.game_id"], name="fk_session_history_game_id"),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.session_id"], name="fk_session_history_session_id")
    )

    # Tạo bảng child_progress
    op.create_table(
        "child_progress",
        sa.Column("progress_id", mssqlUUID(), nullable=False, server_default=sa.text("NEWID()")),
        sa.Column("child_id", mssqlUUID(), nullable=False),
        sa.Column("game_id", mssqlUUID(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("accuracy", sa.Float(), nullable=False),
        sa.Column("avg_response_time", sa.Float(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("last_played", DATETIME2(), nullable=False),
        sa.Column("ratio", NVARCHAR(1000), nullable=False, server_default="[]"),
        sa.Column("review_emotions", NVARCHAR(1000), nullable=False, server_default="[]"),
        sa.PrimaryKeyConstraint("progress_id"),
        sa.ForeignKeyConstraint(["child_id"], ["children.user_id"], name="fk_child_progress_child_id"),
        sa.ForeignKeyConstraint(["game_id"], ["games.game_id"], name="fk_child_progress_game_id")
    )

    # Tạo bảng game_history
    op.create_table(
        "game_history",
        sa.Column("history_id", mssqlUUID(), nullable=False, server_default=sa.text("NEWID()")),
        sa.Column("user_id", mssqlUUID(), nullable=False),
        sa.Column("session_id", mssqlUUID(), nullable=False),
        sa.Column("game_id", mssqlUUID(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("history_id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], name="fk_game_history_user_id"),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.session_id"], name="fk_game_history_session_id"),
        sa.ForeignKeyConstraint(["game_id"], ["games.game_id"], name="fk_game_history_game_id")
    )

    # Tạo bảng reports
    op.create_table(
        "reports",
        sa.Column("report_id", mssqlUUID(), nullable=False, server_default=sa.text("NEWID()")),
        sa.Column("child_id", mssqlUUID(), nullable=False),
        sa.Column("report_type", sa.Enum("daily", "weekly", "monthly", name="report_type_enum"), nullable=False),
        sa.Column("generated_at", DATETIME2(), nullable=False),
        sa.Column("summary", NVARCHAR(1000), nullable=False),
        sa.Column("data", NVARCHAR(1000), nullable=False),
        sa.PrimaryKeyConstraint("report_id"),
        sa.ForeignKeyConstraint(["child_id"], ["children.user_id"], name="fk_reports_child_id")
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("reports")
    op.drop_table("game_history")
    op.drop_table("child_progress")
    op.drop_table("session_questions")
    op.drop_table("sessions")
    op.drop_table("session_history")  # Thêm dòng này
    op.drop_table("emotion_concepts")
    op.drop_table("game_data_contents")
    op.drop_table("game_data")
    op.drop_table("question_answer_options")
    op.drop_table("questions")
    op.drop_table("game_content")
    op.drop_table("games")
    op.drop_table("children")
    op.drop_table("users")