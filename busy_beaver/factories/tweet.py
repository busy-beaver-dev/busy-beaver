import factory
from busy_beaver.adapters.twitter import Tweet


def TweetFactory(session):
    class _TweetFactory(factory.Factory):
        class Meta:
            model = Tweet

        id = factory.Sequence(lambda n: n)

    return _TweetFactory
