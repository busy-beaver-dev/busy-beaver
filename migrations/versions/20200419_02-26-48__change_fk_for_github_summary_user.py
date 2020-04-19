"""relate github summary config to github users

Revision ID: 8906cc54f4cd
Revises: 6d128f97bf34
Create Date: 2020-04-19 00:53:53.206962

"""
from alembic import op
import sqlalchemy as sa

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
    # Given installation_id, update config_id
    engine = op.get_bind()
    meta = sa.MetaData(bind=engine)
    slack_installation = sa.Table("slack_installation", meta, autoload=True)
    github_summary_config = sa.Table(
        "github_summary_configuration", meta, autoload=True
    )
    stmt = sa.select([slack_installation.c.id, github_summary_config.c.id]).select_from(
        sa.join(
            slack_installation,
            github_summary_config,
            slack_installation.c.id == github_summary_config.c.installation_id,
        )
    )
    result = engine.execute(stmt).fetchall()

    github_summary_user = sa.Table("github_summary_user", meta, autoload=True)
    for installation_id, config_id in result:
        stmt = (
            github_summary_user.update()
            .values(config_id=config_id)
            .where(github_summary_user.c.installation_id == installation_id)
        )
        engine.execute(stmt)

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
    engine = op.get_bind()
    meta = sa.MetaData(bind=engine)
    slack_installation = sa.Table("slack_installation", meta, autoload=True)
    github_summary_config = sa.Table(
        "github_summary_configuration", meta, autoload=True
    )
    stmt = sa.select([slack_installation.c.id, github_summary_config.c.id]).select_from(
        sa.join(
            slack_installation,
            github_summary_config,
            slack_installation.c.id == github_summary_config.c.installation_id,
        )
    )
    result = engine.execute(stmt).fetchall()

    github_summary_user = sa.Table("github_summary_user", meta, autoload=True)
    for installation_id, config_id in result:
        stmt = (
            github_summary_user.update()
            .values(installation_id=installation_id)
            .where(github_summary_user.c.config_id == config_id)
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
