from datetime import datetime
from typing import List, NamedTuple

import tweepy
import pytz

from ..config import TWITTER_USERNAME


class Tweet(NamedTuple):
    id_: int
    created_at: datetime


class TwitterAdapter:
    def __init__(self, consumer_key, consumer_secret, token, token_secret):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(token, token_secret)
        self.client = tweepy.API(auth)

    def get_user_timeline(self, username: str) -> List[Tweet]:
        tweets = self.client.user_timeline(screen_name=username, tweet_mode="extended")
        cleaned_tweets = []
        for tweet in tweets:
            dt = pytz.utc.localize(tweet.created_at)
            cleaned_tweets.append(Tweet(id_=tweet.id, created_at=dt))
        return cleaned_tweets

    def get_last_tweet_id(self, username: str = TWITTER_USERNAME) -> int:
        tweets = self.client.user_timeline(screen_name=username, tweet_mode="extended")
        return tweets[0].id
