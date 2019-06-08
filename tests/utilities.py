from unittest import mock


class FakeSlackClient:
    def __init__(self, *, channel_info=None):
        self.mock = mock.MagicMock()
        if channel_info:
            self.channel_info = channel_info

    def get_channel_info(self, *args, **kwargs):
        self.mock(*args, **kwargs)
        return self.channel_info

    def post_message(self, *args, **kwargs):
        self.mock(*args, **kwargs)
        return

    def __repr__(self):
        return "<FakeSlackClient>"
