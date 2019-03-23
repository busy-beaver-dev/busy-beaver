import logging

from flask import request
from flask.views import MethodView
from sqlalchemy import desc

from busy_beaver import config, slack
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
        data = request.json
        if not data or "channel" not in data:
            logger.error(
                "[Busy-Beaver] Youtube Video Poll -- need channel in JSON body"
            )
            return make_response(
                400, json={"run": "incomplete"}, error="Missing Channel"
            )
        self.channel = data["channel"]
        youtube = YoutubeAdapter(api_key=config.YOUTUBE_API_KEY)
        videos = youtube.get_latest_videos_from_channel(config.YOUTUBE_CHANNEL)
        self.parse_and_post_videos(videos)
        return make_response(200, json={"run": "complete"})

    def parse_and_post_videos(self, videos):
        last_video = YoutubeVideo.query.order_by(desc("published_at")).first()
        if not last_video:
            self.save_and_post_video(videos[0])
            return
        for video in videos:
            published_str = video["snippet"]["publishedAt"]
            published_dt = YoutubeVideo.date_str_to_datetime(published_str)
            if last_video.published_at < published_dt:
                self.save_and_post_video(video)
            else:
                break

    def save_and_post_video(self, video):
        video_title = video["snippet"]["title"]
        video_id = video["id"]["videoId"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        msg = f"[Busy-Beaver] Youtube Video Poll -- posting {video_title}"
        logger.info(msg)
        youtube_video = YoutubeVideo(
            youtube_id=video_id,
            title=video_title,
            published_at=video["snippet"]["publishedAt"],
            description=video["snippet"]["description"],
        )
        db.session.add(youtube_video)
        db.session.commit()
        slack_msg = f"A new video has been released: {video_url}"
        slack.post_message(slack_msg, channel=self.channel)
