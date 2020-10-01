"""add cascade delete to foreign key relationships

Revision ID: b99005e9733d
Revises: 1fe0aa535040
Create Date: 2020-10-01 19:05:34.770544

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "b99005e9733d"
down_revision = "1fe0aa535040"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "fk_installation_id", "call_for_proposals_configuration", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_installation_id",
        "call_for_proposals_configuration",
        "slack_installation",
        ["installation_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "fk_installation_id", "github_summary_configuration", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_installation_id",
        "github_summary_configuration",
        "slack_installation",
        ["installation_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "fk_github_summary_configuration_id", "github_summary_user", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_github_summary_configuration_id",
        "github_summary_user",
        "github_summary_configuration",
        ["config_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint("fk_installation_id", "slack_user", type_="foreignkey")
    op.create_foreign_key(
        "fk_installation_id",
        "slack_user",
        "slack_installation",
        ["installation_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "fk_installation_id", "upcoming_events_configuration", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_installation_id",
        "upcoming_events_configuration",
        "slack_installation",
        ["installation_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "fk_upcoming_events_configuration_id",
        "upcoming_events_group",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_upcoming_events_configuration_id",
        "upcoming_events_group",
        "upcoming_events_configuration",
        ["config_id"],
        ["id"],
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "fk_upcoming_events_configuration_id",
        "upcoming_events_group",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_upcoming_events_configuration_id",
        "upcoming_events_group",
        "upcoming_events_configuration",
        ["config_id"],
        ["id"],
    )
    op.drop_constraint(
        "fk_installation_id", "upcoming_events_configuration", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_installation_id",
        "upcoming_events_configuration",
        "slack_installation",
        ["installation_id"],
        ["id"],
    )
    op.drop_constraint("fk_installation_id", "slack_user", type_="foreignkey")
    op.create_foreign_key(
        "fk_installation_id",
        "slack_user",
        "slack_installation",
        ["installation_id"],
        ["id"],
    )
    op.drop_constraint(
        "fk_github_summary_configuration_id", "github_summary_user", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_github_summary_configuration_id",
        "github_summary_user",
        "github_summary_configuration",
        ["config_id"],
        ["id"],
    )
    op.drop_constraint(
        "fk_installation_id", "github_summary_configuration", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_installation_id",
        "github_summary_configuration",
        "slack_installation",
        ["installation_id"],
        ["id"],
    )
    op.drop_constraint(
        "fk_installation_id", "call_for_proposals_configuration", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_installation_id",
        "call_for_proposals_configuration",
        "slack_installation",
        ["installation_id"],
        ["id"],
    )
    # ### end Alembic commands ###
