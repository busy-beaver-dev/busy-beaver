from redis.exceptions import RedisError
from rq.exceptions import NoSuchJobError
from rq.job import Job
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_utils import ChoiceType

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


class Task(BaseModel):
    """Task Base Table"""

    __tablename__ = "task"

    class TaskState:
        COMPLETED = "completed"
        SCHEDULED = "scheduled"
        FAILED = "failed"
        CANCELLED = "cancelled"

        STATES = [(COMPLETED,) * 2, (SCHEDULED,) * 2, (FAILED,) * 2, (CANCELLED,) * 2]
        INITIAL_STATE = SCHEDULED

    # Attributes
    job_id = db.Column(db.String(36), index=True)
    name = db.Column(db.String(128), index=True)
    task_state = db.Column(
        ChoiceType(TaskState.STATES), default=TaskState.INITIAL_STATE, index=True
    )
    data = db.Column(db.JSON)
    time_to_post = db.Column(db.String(20), nullable=True)

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
