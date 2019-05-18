from datetime import datetime

from busy_beaver.extensions import db
from . import BaseModel


class YoutubeVideo(BaseModel):
    """YoutubeVide table"""

    __tablename__ = "youtube_video"

    def __repr__(self):
        return f"<YoutubeVideo({self.youtube_id})>"

    # Attributes
    youtube_id = db.Column(db.String(300), nullable=False)

    title = db.Column(db.String(300), nullable=False)
    published_at = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.String(1000), nullable=False)

    @staticmethod
    def date_str_to_datetime(date_str: str) -> datetime:
        """For converting string 'publishedAt'."""
        date_format = "%Y-%m-%dT%H:%M:%S"
        return datetime.strptime(date_str.split(".")[0], date_format)
