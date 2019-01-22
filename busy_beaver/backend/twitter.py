from typing import List

from tweepy.models import Status


class TwitterAdapter:
    def __init__(self, client):
        self.client = client

    def get_user_timeline(self, username: str) -> List[Status]:
        return self.client.user_timeline(screen_name=username, tweet_mode="extended")
