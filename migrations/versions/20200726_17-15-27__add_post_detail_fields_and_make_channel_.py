"""add post detail fields and make channel non-nullable

Revision ID: 50cefad49d98
Revises: 7959c628791e
Create Date: 2020-07-26 17:15:27.050405

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

# revision identifiers, used by Alembic.
revision = "50cefad49d98"
down_revision = "7959c628791e"
branch_labels = None
depends_on = None


# decided to hard code it here since this is dependent on the migration
WEEKDAYS = [
    ("Sunday",) * 2,
    ("Monday",) * 2,
    ("Tuesday",) * 2,
    ("Wednesday",) * 2,
    ("Thursday",) * 2,
    ("Friday",) * 2,
    ("Saturday",) * 2,
]


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "upcoming_events_configuration",
        sa.Column(
            "post_day_of_week",
            sqlalchemy_utils.types.choice.ChoiceType(choices=WEEKDAYS),
            nullable=False,
        ),
    )
    op.add_column(
        "upcoming_events_configuration",
        sa.Column("post_num_events", sa.Integer(), nullable=False),
    )
    op.add_column(
        "upcoming_events_configuration",
        sa.Column("post_time", sa.Time(), nullable=False),
    )
    op.add_column(
        "upcoming_events_configuration",
        sa.Column(
            "post_timezone",
            sqlalchemy_utils.types.timezone.TimezoneType(backend="pytz"),
            nullable=False,
        ),
    )
    op.alter_column(
        "upcoming_events_configuration",
        "channel",
        existing_type=sa.VARCHAR(length=20),
        nullable=False,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "upcoming_events_configuration",
        "channel",
        existing_type=sa.VARCHAR(length=20),
        nullable=True,
    )
    op.drop_column("upcoming_events_configuration", "post_timezone")
    op.drop_column("upcoming_events_configuration", "post_time")
    op.drop_column("upcoming_events_configuration", "post_num_events")
    op.drop_column("upcoming_events_configuration", "post_day_of_week")
    # ### end Alembic commands ###
