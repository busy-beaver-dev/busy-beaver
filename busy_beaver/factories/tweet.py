import factory
from busy_beaver.adapters.twitter import Tweet


class TweetFactory(factory.Factory):
    class Meta:
        model = Tweet

    id = factory.Sequence(lambda n: n)
