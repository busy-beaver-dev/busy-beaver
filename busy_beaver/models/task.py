from redis.exceptions import RedisError
from rq.exceptions import NoSuchJobError
from rq.job import Job

from . import BaseModel
from busy_beaver.extensions import db, rq


class Task(BaseModel):
    """Task Base Table"""

    def __repr__(self):
        return f"<Task: {self.id}-{self.name}>"

    # Attributes
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    failed = db.Column(db.Boolean, default=False)
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            rq_job = Job.fetch(self.id, rq.connection)
        except (RedisError, NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get("progress", 0) if job is not None else 100
