from redis.exceptions import RedisError
from rq.exceptions import NoSuchJobError
from rq.job import Job
from sqlalchemy.ext.declarative import declared_attr

from busy_beaver.extensions import db, rq


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime,
        onupdate=db.func.current_timestamp(),
        default=db.func.current_timestamp(),
    )

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def patch(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)


class KeyValueStore(BaseModel):
    """Key Value store by slack workspace id

    Keeps track of required values for each workspace"""

    __tablename__ = "key_value_store"

    def __repr__(self):  # pragma: no cover
        workspace_name = self.slack_installation.workspace_name
        return f"<KeyValueStore: {workspace_name} {self.key} {self.value}>"

    # Attributes
    installation_id = db.Column(
        db.Integer,
        db.ForeignKey("slack_installation.id", name="fk_installation_id"),
        nullable=False,
    )
    key = db.Column(db.String(255), nullable=False, unique=True)
    value = db.Column(db.LargeBinary(), nullable=False)

    # Relationships
    slack_installation = db.relationship(
        "SlackInstallation", back_populates="key_value_pairs"
    )


class Task(BaseModel):
    """Task Base Table"""

    __tablename__ = "task"

    # Attributes
    job_id = db.Column(db.String(36), index=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    failed = db.Column(db.Boolean, default=False)
    complete = db.Column(db.Boolean, default=False)
    type = db.Column(db.String(55))

    __mapper_args__ = {"polymorphic_identity": "task", "polymorphic_on": "type"}

    def get_rq_job(self):
        try:
            rq_job = Job.fetch(self.job_id, rq.connection)
        except (RedisError, NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get("progress", 0) if job is not None else 100

    def __repr__(self):  # pragma: no cover
        return f"<Task: {self.job_id}-{self.name}>"
