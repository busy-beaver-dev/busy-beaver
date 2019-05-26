"""change column name and add end_epoch in event table

Revision ID: ad8d0445e832
Revises: 958548ca6d07
Create Date: 2019-05-26 22:47:39.821526

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ad8d0445e832"
down_revision = "958548ca6d07"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "event", "utc_epoch", new_column_name="start_epoch", server_default=None
    )
    op.add_column("event", sa.Column("end_epoch", sa.Integer(), nullable=True))

    # copy start_epoch to end_epoch
    # alter column to nullable = False
    op.alter_column("event", "end_epoch", nullable=False)


def downgrade():
    op.alter_column(
        "event", "start_epoch", new_column_name="utc_epoch", server_default=None
    )
    op.drop_column("event", "end_epoch")
