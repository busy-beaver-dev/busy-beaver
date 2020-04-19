from redis.exceptions import RedisError
from rq.exceptions import NoSuchJobError
from rq.job import Job

from busy_beaver.common.models import BaseModel
from busy_beaver.extensions import db, rq


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


class PostGitHubSummaryTask(Task):
    """This is not used...

    Keeping it around as an example of how to do things.
    """

    __tablename__ = "post_github_summary_task"

    # Attributes
    id = db.Column(db.Integer, db.ForeignKey("task.id"), primary_key=True)
    data = db.Column("data", db.JSON)

    __mapper_args__ = {"polymorphic_identity": "post_github_summary"}

    def __repr__(self):  # pragma: no cover
        return f"<PostGitHubSummaryTask: {self.data}>"


class PostTweetTask(Task):
    """This is not used...

    Keeping it around as an example of how to do things.
    """

    __tablename__ = "post_tweet_task"

    # Attributes
    id = db.Column(db.Integer, db.ForeignKey("task.id"), primary_key=True)
    data = db.Column("data", db.JSON)

    __mapper_args__ = {"polymorphic_identity": "post_tweet"}

    def __repr__(self):  # pragma: no cover
        return f"<PostTweetTask: {self.data}>"


class SyncEventDatabaseTask(Task):
    """This is not used...

    Keeping it around as an example of how to do things.
    """

    __tablename__ = "sync_event_database_task"

    # Attributes
    id = db.Column(db.Integer, db.ForeignKey("task.id"), primary_key=True)
    data = db.Column("data", db.JSON)

    __mapper_args__ = {"polymorphic_identity": "sync_event_database"}

    def __repr__(self):  # pragma: no cover
        return f"<SyncEventDatabaseTask: {self.data}>"
