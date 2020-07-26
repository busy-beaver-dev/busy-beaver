from finite_state_machine import StateMachine, transition
from finite_state_machine.exceptions import ConditionNotMet
from sqlalchemy_utils import ChoiceType, TimezoneType

from busy_beaver.common.models import BaseModel
from busy_beaver.exceptions import StateMachineError
from busy_beaver.extensions import db

WEEKDAYS = [
    ("Sunday",) * 2,
    ("Monday",) * 2,
    ("Tuesday",) * 2,
    ("Wednesday",) * 2,
    ("Thursday",) * 2,
    ("Friday",) * 2,
    ("Saturday",) * 2,
]


class UpcomingEventsEnabledStateMachine(StateMachine):
    initial_state = False

    def __init__(self, config):
        self.config = config
        self.state = config.enabled
        super().__init__()

    @transition(source=False, target=True)
    def enable_feature(self):
        pass

    @transition(source=True, target=False)
    def disable_feature(self):
        pass

    def toggle(self):
        if self.state:
            self.disable_feature()
        else:
            self.enable_feature()


class UpcomingEventsConfiguration(BaseModel):
    __tablename__ = "upcoming_events_configuration"

    def __repr__(self):  # pragma: no cover
        return (
            f"<UpcomingEventsConfiguration: {self.slack_installation.workspace_name}>"
        )

    enabled = db.Column(db.Boolean, default=False, nullable=False)
    installation_id = db.Column(
        db.Integer,
        db.ForeignKey("slack_installation.id", name="fk_installation_id"),
        nullable=False,
    )
    channel = db.Column(db.String(20), nullable=False)
    post_day_of_week = db.Column(ChoiceType(WEEKDAYS), nullable=False)
    post_time = db.Column(db.Time, nullable=False)
    post_timezone = db.Column(TimezoneType(backend="pytz"), nullable=False)
    post_num_events = db.Column(db.Integer, nullable=False)

    # Relationships
    slack_installation = db.relationship(
        "SlackInstallation", back_populates="upcoming_events_config"
    )
    groups = db.relationship("UpcomingEventsGroup", back_populates="configuration")

    def toggle_enabled(self):
        machine = UpcomingEventsEnabledStateMachine(self)
        try:
            machine.toggle()
        except ConditionNotMet as e:
            raise StateMachineError(f"Condition failed: {e.condition.__name__}")
        self.enabled = machine.state


class UpcomingEventsGroup(BaseModel):
    """Meetup Groups associated with the Upcoming Events Configuration

    - each Slack workspace can have 0/1 Upcoming Events configurations
    - each event configuration can be set for 1+ meetup groups
    """

    __tablename__ = "upcoming_events_group"

    def __repr__(self):  # pragma: no cover
        return f"<UpcomingEventsGroup: {self.meetup_urlname}>"

    config_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "upcoming_events_configuration.id",
            name="fk_upcoming_events_configuration_id",
        ),
        nullable=False,
    )
    meetup_urlname = db.Column(db.String(100), nullable=False)

    # Relationships
    configuration = db.relationship(
        "UpcomingEventsConfiguration", back_populates="groups"
    )
    events = db.relationship("Event", back_populates="group")


class Event(BaseModel):
    """Event table for storing information about past and future meetups"""

    __tablename__ = "event"

    def __repr__(self):  # pragma: no cover
        return f"<Event: {self.name}>"

    # Attributes
    group_id = db.Column(
        db.Integer,
        db.ForeignKey("upcoming_events_group.id", name="fk_upcoming_events_group_id"),
        nullable=False,
    )

    remote_id = db.Column(db.String(255), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    venue = db.Column(db.String(255), nullable=False)
    start_epoch = db.Column(db.Integer, nullable=False)
    end_epoch = db.Column(db.Integer, nullable=False)

    # Relationships
    group = db.relationship("UpcomingEventsGroup", back_populates="events")
