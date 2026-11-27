"""tabel gold set: gold_items dan gold_labels

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "gold_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "review_id",
            sa.BigInteger(),
            sa.ForeignKey("reviews.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("peluang_terpilih", sa.Float(), nullable=False),
        sa.Column("bobot", sa.Float(), nullable=False),
        sa.Column("seed", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "gold_labels",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "review_id",
            sa.BigInteger(),
            sa.ForeignKey("reviews.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("putaran", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("label", sa.String(10), nullable=False),
        sa.Column("tipe", sa.String(20), nullable=False, server_default="biasa"),
        sa.Column("ragu", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("catatan", sa.Text(), nullable=True),
        sa.Column("annotator", sa.String(50), nullable=False, server_default="penulis"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("review_id", "putaran", name="uq_gold_labels_review_putaran"),
        sa.CheckConstraint(
            "label IN ('negatif', 'netral', 'positif')", name="ck_gold_labels_label"
        ),
        sa.CheckConstraint("putaran IN (1, 2)", name="ck_gold_labels_putaran"),
    )


def downgrade() -> None:
    op.drop_table("gold_labels")
    op.drop_table("gold_items")
