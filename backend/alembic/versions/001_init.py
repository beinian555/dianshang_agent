"""initial database schema

Revision ID: 001
Revises:
Create Date: 2026-06-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("category", sa.String(), server_default="beauty"),
        sa.Column("platform", sa.String(), server_default="unknown"),
        sa.Column("product", postgresql.JSONB(), nullable=True),
        sa.Column("competitors", postgresql.JSONB(), nullable=True),
        sa.Column("reviews", postgresql.JSONB(), nullable=True),
        sa.Column("weekly_metrics", postgresql.JSONB(), nullable=True),
        sa.Column("reports", postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.String(), server_default="draft"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "analysis_jobs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("project_id", sa.String(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("status", sa.String(), server_default="pending"),
        sa.Column("progress", sa.Integer(), server_default="0"),
        sa.Column("current_step", sa.String(), nullable=True),
        sa.Column("report_id", sa.String(), nullable=True),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analysis_jobs_project_id", "analysis_jobs", ["project_id"])

    op.create_table(
        "llm_call_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("agent_name", sa.String(), server_default=""),
        sa.Column("provider", sa.String(), server_default=""),
        sa.Column("model", sa.String(), nullable=True),
        sa.Column("call_type", sa.String(), server_default="generate_json"),
        sa.Column("latency_ms", sa.Float(), server_default="0.0"),
        sa.Column("success", sa.Boolean(), server_default=sa.true()),
        sa.Column("fallback_used", sa.Boolean(), server_default=sa.false()),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column("prompt_length", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("llm_call_logs")
    op.drop_table("analysis_jobs")
    op.drop_table("projects")
