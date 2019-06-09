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
    # Step 1: Schema migration
    # Change column name (to start_epoch) and add end_epoch column
    op.alter_column(
        "event", "utc_epoch", new_column_name="start_epoch", server_default=None
    )
    op.add_column("event", sa.Column("end_epoch", sa.Integer(), nullable=True))

    # Step 2: Data migration
    # Set end_epoch col to start_epoch col
    engine = op.get_bind()
    meta = sa.MetaData(bind=engine)
    event = sa.Table("event", meta, autoload=True)
    stmt = event.update().values(end_epoch=event.c.start_epoch)
    engine.execute(stmt)

    # Step 3: Schema migration
    # end_epoch column can't be empty
    op.alter_column("event", "end_epoch", nullable=False)

    # Step 4: Schema migration
    # rename table
    op.rename_table("fetch_new_events_task", "fetch_events_task")


def downgrade():
    op.alter_column(
        "event", "start_epoch", new_column_name="utc_epoch", server_default=None
    )
    op.drop_column("event", "end_epoch")

    op.rename_table("fetch_events_task", "fetch_new_events_task")
