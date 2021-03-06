"""make group_id non-nullable after data migration

Revision ID: 68ff4349ae47
Revises: f29c0fd74c68
Create Date: 2020-07-12 19:59:28.800930

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "68ff4349ae47"
down_revision = "f29c0fd74c68"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("event", "group_id", existing_type=sa.INTEGER(), nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("event", "group_id", existing_type=sa.INTEGER(), nullable=True)
    # ### end Alembic commands ###
