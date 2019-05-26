from collections import namedtuple
from datetime import datetime
from typing import Dict

from .requests_client import RequestsClient, Response
from busy_beaver.models import YouTubeVideo


def sort_by_published(video_json: Dict) -> datetime:
    publish_at = video_json["snippet"]["publishedAt"].split(".")[0]
    return YouTubeVideo.date_str_to_datetime(publish_at)


class YouTubeAdapter:
    def __init__(self, *, api_key: str) -> None:
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.api_key = api_key
        self.client = RequestsClient()

    def __repr__(self) -> str:
        return "YouTubeAdapter()"

    def __str__(self) -> str:
        return "YouTubeAdapter"

    def get_latest_videos_from_channel(self, channel_id: str) -> Response:
        params = {
            "channelId": channel_id,
            "key": self.api_key,
            "part": "snippet,id",
            "order": "date",
            "maxResults": 50,
            "type": "video",
        }
        url = f"{self.base_url}/search"
        response = self.client.get(url, params=params)

        # Unpack and label items in response
        labels = namedtuple("YoutubeVideo", ["url", "name", "date"])

        results = [
            labels(
                *[
                    "https://www.youtube.com/watch?v=" + _["id"]["videoId"],
                    _["snippet"]["title"],
                    _["snippet"]["publishedAt"],
                ]
            )
            for _ in response.json["items"]
            if _["id"]["kind"] == "youtube#video"
        ]

        return results

        # TODO
        # THIS WAS THE ORIGINAL, figure out how this works with tests
        # merging a stale branch where two folks worked on the same feature
        # resp = self.client.get(url, params=params)
        # videos_json = resp.json["items"]
        # return sorted(videos_json, reverse=True, key=sort_by_published)
