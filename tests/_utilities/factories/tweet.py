import factory
from busy_beaver.adapters.twitter import Tweet as model


def Tweet(session):
    class _TweetFactory(factory.Factory):
        class Meta:
            model = model

        id = factory.Sequence(lambda n: n)

    return _TweetFactory
