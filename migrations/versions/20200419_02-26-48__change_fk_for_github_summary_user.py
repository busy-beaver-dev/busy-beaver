"""relate github summary config to github users

Revision ID: 8906cc54f4cd
Revises: 6d128f97bf34
Create Date: 2020-04-19 00:53:53.206962

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm.session import Session

from busy_beaver.models import GitHubSummaryUser

# revision identifiers, used by Alembic.
revision = "8906cc54f4cd"
down_revision = "6d128f97bf34"
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Schema migration
    # Add column to store config_id
    op.add_column(
        "github_summary_user", sa.Column("config_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        "fk_github_summary_configuration_id",
        "github_summary_user",
        "github_summary_configuration",
        ["config_id"],
        ["id"],
    )

    # Step 2: Data migration
    # Given Slack installation, set the config_id foreign key
    session = Session(bind=op.get_bind())

    users = session.query(GitHubSummaryUser).all()
    for user in users:
        user.configuration = user.installation.github_summary_config
        session.add(user)
    session.commit()

    # Step 3: Schema migration
    # Ensure config_id foreign_key cannot be empty
    op.alter_column(
        "github_summary_user", "config_id", existing_type=sa.INTEGER(), nullable=False
    )

    # Step 4: Schema migration
    # Remove Slack installation foreign key relation
    op.drop_constraint("fk_installation_id", "github_summary_user", type_="foreignkey")
    op.drop_column("github_summary_user", "installation_id")


def downgrade():
    # Step 1: Schema migration
    # Add Slack installation foreign key
    op.add_column(
        "github_summary_user",
        sa.Column("installation_id", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.create_foreign_key(
        "fk_installation_id",
        "github_summary_user",
        "slack_installation",
        ["installation_id"],
        ["id"],
    )

    # Step 2: Data migration
    # Given GitHub configuration, set the installation_id foreign key
    engine = engine = op.get_bind()
    meta = sa.MetaData(bind=engine)
    github_summary_user = sa.Table("github_summary_user", meta, autoload=True)

    session = Session(bind=engine)

    users = session.query(GitHubSummaryUser).all()
    for user in users:
        stmt = (
            github_summary_user.update()
            .values(installation_id=user.configuration.installation_id)
            .where(github_summary_user.c.id == user.id)
        )
        engine.execute(stmt)

    # Step 3: Schema migration
    # Ensure installation_id foreign_key cannot be empty
    op.alter_column(
        "github_summary_user",
        "installation_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )

    # Step 3: Schema migration
    # Drop config_id Foreign Key
    op.drop_constraint(
        "fk_github_summary_configuration_id", "github_summary_user", type_="foreignkey"
    )
    op.drop_column("github_summary_user", "config_id")
