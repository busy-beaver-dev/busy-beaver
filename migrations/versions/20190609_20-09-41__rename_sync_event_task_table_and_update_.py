"""rename sync event task table and update values

Revision ID: 383bbb33f257
Revises: ad8d0445e832
Create Date: 2019-06-09 20:09:41.764048

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "383bbb33f257"
down_revision = "ad8d0445e832"
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Schema migration
    # rename table
    op.rename_table("fetch_new_events_task", "sync_event_database_task")

    # Step 2: Data migration
    # Change task type to new sync_task_name
    engine = op.get_bind()
    meta = sa.MetaData(bind=engine)
    task = sa.Table("task", meta, autoload=True)
    stmt = (
        task.update()
        .where(task.c.type == "fetch_new_events")
        .values(type="sync_event_database")
    )
    engine.execute(stmt)


def downgrade():
    op.rename_table("sync_event_database_task", "fetch_new_events_task")

    engine = op.get_bind()
    meta = sa.MetaData(bind=engine)
    task = sa.Table("task", meta, autoload=True)
    stmt = (
        task.update()
        .where(task.c.type == "sync_event_database")
        .values(type="fetch_new_events")
    )
    engine.execute(stmt)
