"""skema awal: apps, app_versions, reviews

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "apps",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("package_name", sa.String(200), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "app_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "app_id",
            sa.Integer(),
            sa.ForeignKey("apps.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version_name", sa.String(50), nullable=False),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("app_id", "version_name", name="uq_app_versions"),
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "app_id",
            sa.Integer(),
            sa.ForeignKey("apps.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("external_id", sa.String(100), nullable=False, unique=True),
        sa.Column("user_hash", sa.String(64), nullable=False),
        sa.Column("rating", sa.SmallInteger(), nullable=False),
        sa.Column("text_raw", sa.Text(), nullable=False),
        sa.Column("thumbs_up", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("app_version", sa.String(50), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "scraped_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("lang", sa.String(10), nullable=True),
        sa.Column("exclude_reason", sa.String(30), nullable=True),
        sa.CheckConstraint("rating BETWEEN 1 AND 5", name="ck_reviews_rating"),
    )
    op.create_index("ix_reviews_reviewed_at", "reviews", ["reviewed_at"])
    op.create_index("ix_reviews_app_version", "reviews", ["app_version"])


def downgrade() -> None:
    op.drop_index("ix_reviews_app_version", table_name="reviews")
    op.drop_index("ix_reviews_reviewed_at", table_name="reviews")
    op.drop_table("reviews")
    op.drop_table("app_versions")
    op.drop_table("apps")
