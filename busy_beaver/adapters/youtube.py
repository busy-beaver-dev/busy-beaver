from collections import namedtuple

from .requests_client import RequestsClient, Response


class YoutubeAdapter:
    def __init__(self, *, api_key: str) -> None:
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.api_key = api_key
        self.client = RequestsClient()

    def __repr__(self) -> str:
        return "YoutubeAdapter()"

    def __str__(self) -> str:
        return "YoutubeAdapter"

    def get_latest_videos_from_channel(self, channel_id: str) -> Response:
        params = {
            "channelId": channel_id,
            "key": self.api_key,
            "part": "snippet,id",
            "order": "date",
        }
        url = f"{self.base_url}/search"
        response = self.client.get(url, params=params)

        # Unpack and label items in response 
        labels = namedtuple("YoutubeVideo", ["url", "name", "date"])

        results = [labels(
            *["https://www.youtube.com/watch?v=" + _["id"]["videoId"],
            _["snippet"]["title"], 
            _["snippet"]["publishedAt"]
            ]) for _ in response.json['items'] if _["id"]["kind"] == "youtube#video"]

        return results