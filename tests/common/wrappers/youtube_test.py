import pytest

from busy_beaver.common.wrappers.youtube import YouTubeClient
from busy_beaver.config import YOUTUBE_API_KEY, YOUTUBE_CHANNEL


@pytest.fixture
def client():
    yield YouTubeClient(api_key=YOUTUBE_API_KEY)


@pytest.mark.vcr()
def test_get_latest_videos_from_channel(client):
    response = client.get_latest_videos_from_channel(channel_id=YOUTUBE_CHANNEL)
    assert response[0][0] == "https://www.youtube.com/watch?v=J3XYnnHrumM"
    assert response[0][1] == "chipy org sprint sponsored by quicket solutions"
    assert response[0][2] == "2019-04-16T15:05:28.000Z"
