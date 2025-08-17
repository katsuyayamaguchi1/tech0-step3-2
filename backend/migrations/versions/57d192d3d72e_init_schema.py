"""init schema

Revision ID: 57d192d3d72e
Revises: cfcdf299ed2f
Create Date: 2025-08-17 10:04:16.742770
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "57d192d3d72e"
down_revision: Union[str, None] = "cfcdf299ed2f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # create only the 'sample' table (no drops of existing tables)
    op.create_table(
        "sample",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sample")),
    )


def downgrade() -> None:
    # on downgrade, just drop the 'sample' table
    op.drop_table("sample")
