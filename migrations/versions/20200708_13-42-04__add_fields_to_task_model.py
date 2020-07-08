"""add fields to task model

Revision ID: 021c59bef200
Revises: 6ca59a92db5c
Create Date: 2020-07-08 13:42:04.480472

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

from busy_beaver.common.models import Task

# revision identifiers, used by Alembic.
revision = "021c59bef200"
down_revision = "6ca59a92db5c"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("task", sa.Column("data", sa.JSON(), nullable=True))
    op.add_column(
        "task",
        sa.Column(
            "task_state",
            sqlalchemy_utils.types.choice.ChoiceType(Task.TaskState.STATES),
            nullable=True,
        ),
    )
    op.create_index(op.f("ix_task_task_state"), "task", ["task_state"], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_task_task_state"), table_name="task")
    op.drop_column("task", "task_state")
    op.drop_column("task", "data")
    # ### end Alembic commands ###
