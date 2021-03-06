"""add github summary configuration information table

Revision ID: 655741e212e9
Revises: 9bd99c734716
Create Date: 2019-06-29 16:22:57.204498

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "655741e212e9"
down_revision = "9bd99c734716"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "github_summary_configuration",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column("date_modified", sa.DateTime(), nullable=True),
        sa.Column("installation_id", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("time_to_post", sa.String(length=20), nullable=True),
        sa.Column("timezone_info", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["installation_id"], ["slack_installation.id"], name="fk_installation_id"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###

    # Step 1: Schema migration
    # Add column to store state
    op.add_column(
        "slack_installation", sa.Column("state", sa.String(length=20), nullable=True)
    )

    # Step 2: Data migration
    # Set all github_user data to correct installation_id
    engine = op.get_bind()
    meta = sa.MetaData(bind=engine)
    slack_installation = sa.Table("slack_installation", meta, autoload=True)
    stmt = slack_installation.update().values(state="installed")
    engine.execute(stmt)

    # Step 3: Schema migration
    # Ensure installation_id foreign_key cannot be empty
    op.alter_column("slack_installation", "state", nullable=False)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("slack_installation", "state")
    op.drop_table("github_summary_configuration")
    # ### end Alembic commands ###
