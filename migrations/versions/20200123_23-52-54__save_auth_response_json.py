"""save_auth_response_json

Revision ID: 8c5ac2860989
Revises: 655741e212e9
Create Date: 2020-01-23 23:52:54.452643

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8c5ac2860989"
down_revision = "655741e212e9"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "slack_installation", sa.Column("auth_response", sa.JSON(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("slack_installation", "auth_response")
    # ### end Alembic commands ###
