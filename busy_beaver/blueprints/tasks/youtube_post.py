import logging

from flask import request
from flask.views import MethodView

from busy_beaver import config
from busy_beaver.adapters.youtube import YoutubeAdapter
from busy_beaver.toolbox import make_response
from busy_beaver.extensions import db

from busy_beaver.models import YoutubeVideo

logger = logging.getLogger(__name__)

class YoutubePollingResource(MethodView):

    def post(self):
        user = request._internal["user"]
        logger.info(
            "[Busy-Beaver] Youtube Video Poll -- login successful",
            extra={"user": user.username},
        )
        youtube = YoutubeAdapter(api_key=config.YOUTUBE_API_KEY)
        videos = youtube.get_latest_videos_from_channel(config.YOUTUBE_CHANNEL)
        latest_video = videos[0]
        latest_video_id = latest_video['id']['videoId']
        latest_video_published = latest_video['snippet']['publishedAt']
        db_video = YoutubeVideo.query.filter(YoutubeVideo.youtube_id==latest_video_id).first()
        if not db_video:
            youtube_video = YoutubeVideo(
                youtube_id=latest_video_id,
                title=latest_video['snippet']['title'],
                published_at=latest_video_published,
                description=latest_video['snippet']['description']
            )
            db.session.add(youtube_video)
            db.session.commit()
            return 'post to slack'
        if db_video.published_at > YoutubeVideo.date_str_to_datetime(latest_video_published):
            youtube_video = YoutubeVideo(
                youtube_id=latest_video_id,
                title=latest_video['snippet']['title'],
                published_at=latest_video_published,
                description=latest_video['snippet']['description']
            )
            db.session.add(youtube_video)
            db.session.commit()
            return 'post to slack'
        return make_response(200, json={"run": "complete"})
