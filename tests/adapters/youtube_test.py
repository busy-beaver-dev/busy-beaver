import pytest

from busy_beaver.adapters.youtube import YoutubeAdapter
from busy_beaver.config import YOUTUBE_API_TOKEN, YOUTUBE_CHANNEL_ID


@pytest.fixture
def client():
    yield YoutubeAdapter(api_key=YOUTUBE_API_TOKEN)


@pytest.mark.vcr()
def test_get_latest_videos_from_channel(client):
    response = client.get_latest_videos_from_channel(channel_id=YOUTUBE_CHANNEL_ID)
    assert response[0][0] == 'https://www.youtube.com/watch?v=J3XYnnHrumM'
    assert response[0][1] == 'chipy org sprint sponsored by quicket solutions'
    assert response[0][2] == '2019-04-16T15:05:28.000Z'
