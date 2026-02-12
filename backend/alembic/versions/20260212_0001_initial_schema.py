"""initial schema

Revision ID: 20260212_0001
Revises:
Create Date: 2026-02-12 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260212_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("github_id", sa.BigInteger(), nullable=False),
        sa.Column("github_username", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("access_token", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("github_id", name="uq_users_github_id"),
        sa.UniqueConstraint("github_username", name="uq_users_github_username"),
    )
    op.create_index("ix_users_github_id", "users", ["github_id"], unique=False)
    op.create_index("ix_users_github_username", "users", ["github_username"], unique=False)

    op.create_table(
        "github_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("company", sa.String(length=255), nullable=True),
        sa.Column("blog_url", sa.Text(), nullable=True),
        sa.Column("twitter_username", sa.String(length=255), nullable=True),
        sa.Column("public_repos", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("followers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("following", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_stars", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "portfolios",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subdomain", sa.String(length=255), nullable=False),
        sa.Column("custom_domain", sa.String(length=255), nullable=True),
        sa.Column("template_id", sa.String(length=100), nullable=False, server_default="minimal"),
        sa.Column("theme_config", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("last_generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("view_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("generated_html", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("custom_domain", name="uq_portfolios_custom_domain"),
        sa.UniqueConstraint("subdomain", name="uq_portfolios_subdomain"),
    )
    op.create_index("ix_portfolios_subdomain", "portfolios", ["subdomain"], unique=False)

    op.create_table(
        "repositories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("github_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("ai_description", sa.Text(), nullable=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("homepage", sa.Text(), nullable=True),
        sa.Column("language", sa.String(length=100), nullable=True),
        sa.Column("languages", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("topics", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("stars", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("forks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_fork", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_private", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("pushed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("analyzed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("github_id", name="uq_repositories_github_id"),
    )
    op.create_index("ix_repositories_github_id", "repositories", ["github_id"], unique=False)
    op.create_index("ix_repositories_name", "repositories", ["name"], unique=False)
    op.create_index("idx_repos_user_id", "repositories", ["user_id"], unique=False)
    op.create_index("idx_repos_stars", "repositories", [sa.text("stars DESC")], unique=False)
    op.create_index("idx_repos_languages", "repositories", ["languages"], unique=False, postgresql_using="gin")
    op.create_index("idx_repos_topics", "repositories", ["topics"], unique=False, postgresql_using="gin")

    op.create_table(
        "commits",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("repository_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sha", sa.String(length=40), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("author_name", sa.String(length=255), nullable=True),
        sa.Column("author_email", sa.String(length=255), nullable=True),
        sa.Column("committed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("additions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deletions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("files_changed", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sha", name="uq_commits_sha"),
    )
    op.create_index("ix_commits_repository_id", "commits", ["repository_id"], unique=False)
    op.create_index("ix_commits_sha", "commits", ["sha"], unique=False)
    op.create_index("ix_commits_committed_at", "commits", ["committed_at"], unique=False)
    op.create_index("idx_commits_repo_id", "commits", ["repository_id"], unique=False)
    op.create_index("idx_commits_date", "commits", [sa.text("committed_at DESC")], unique=False)

    op.create_table(
        "skills",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("proficiency", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("usage_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_skills_user", "skills", [sa.text("user_id"), sa.text("proficiency DESC")], unique=False)

    op.create_table(
        "analytics_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("event_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("referrer", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["portfolio_id"], ["portfolios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_analytics_portfolio",
        "analytics_events",
        [sa.text("portfolio_id"), sa.text("created_at")],
        unique=False,
    )

    op.create_table(
        "generation_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("progress_percentage", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_step", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["portfolio_id"], ["portfolios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_jobs_status",
        "generation_jobs",
        [sa.text("status"), sa.text("started_at")],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_jobs_status", table_name="generation_jobs")
    op.drop_table("generation_jobs")

    op.drop_index("idx_analytics_portfolio", table_name="analytics_events")
    op.drop_table("analytics_events")

    op.drop_index("idx_skills_user", table_name="skills")
    op.drop_table("skills")

    op.drop_index("idx_commits_date", table_name="commits")
    op.drop_index("idx_commits_repo_id", table_name="commits")
    op.drop_index("ix_commits_committed_at", table_name="commits")
    op.drop_index("ix_commits_sha", table_name="commits")
    op.drop_index("ix_commits_repository_id", table_name="commits")
    op.drop_table("commits")

    op.drop_index("idx_repos_topics", table_name="repositories")
    op.drop_index("idx_repos_languages", table_name="repositories")
    op.drop_index("idx_repos_stars", table_name="repositories")
    op.drop_index("idx_repos_user_id", table_name="repositories")
    op.drop_index("ix_repositories_name", table_name="repositories")
    op.drop_index("ix_repositories_github_id", table_name="repositories")
    op.drop_table("repositories")

    op.drop_index("ix_portfolios_subdomain", table_name="portfolios")
    op.drop_table("portfolios")

    op.drop_table("github_profiles")

    op.drop_index("ix_users_github_username", table_name="users")
    op.drop_index("ix_users_github_id", table_name="users")
    op.drop_table("users")
