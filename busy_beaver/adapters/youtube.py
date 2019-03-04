"""Youtube Adapter.

Docs (TODO: Move into documentation)

Where to get your channel id?

Login to youtube and go to https://www.youtube.com/account_advanced, your
channel id will be displayed.

How to create an api key?

Go to https://console.developers.google.com and create a project. After you can
visit https://developers.google.com/youtube/registering_an_application#Create_API_Keys
for instructions to generate the api key. After you have both, you can move to
the examples.

Example:

api_key = "..."
channel_id = "..."
youtube = YoutubeAdapter(api_key=api_key)
data = youtube.get_latest_videos_from_channel(channel_id)
videos = data["items"]
"""
from typing import Dict

import requests
from IPython import embed


class YoutubeAdapter:
    """Small adapter class to make communication with youtube api."""

    def __init__(self, *, api_key: str) -> None:
        """Initialize with an API Key."""
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.api_key = api_key

    def __repr__(self) -> str:
        """Return repr of instanct."""
        return 'YoutubeAdapter()'

    def __str__(self) -> str:
        """String-ify instance."""
        return 'YoutubeAdapter'

    def get_latest_videos_from_channel(self, channel_id: str) -> Dict:
        """Search Videos."""
        params = {
            "channelId": channel_id,
            "key": self.api_key,
            "part": "snippet,id",
            "order": "date"
        }
        url = f"{self.base_url}/search"
        response = requests.get(url, params=params)
        return response.json()
