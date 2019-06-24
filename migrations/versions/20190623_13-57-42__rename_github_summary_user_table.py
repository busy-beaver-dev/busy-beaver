"""rename github summary user table

Revision ID: dee7af02d018
Revises: 05fd1af68aa4
Create Date: 2019-06-23 13:57:42.112629

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "dee7af02d018"
down_revision = "05fd1af68aa4"
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("user", "github_summary_user")


def downgrade():
    op.rename_table("github_summary_user", "user")
