from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_add_user_points"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("points", sa.Integer(), nullable=False, server_default="0"))
    op.alter_column("users", "points", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "points")

