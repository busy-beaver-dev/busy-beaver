"""Testing helpers that make life easy"""

from unittest import mock


class FakeMeetupAdapter:
    def __init__(self, events):
        self.mock = mock.MagicMock()
        self.events = events

    def get_events(self, *args, **kwargs):
        self.mock(*args, **kwargs)
        return self.events


class FakeSlackClient:
    def __init__(self, *, channel_info=None, timezone_info=None):
        self.mock = mock.MagicMock()
        if channel_info:
            self.channel_info = channel_info
        if timezone_info:
            self.timezone_info = timezone_info

    def __call__(self, *args, **kwargs):
        self.mock(*args, **kwargs)
        return self

    def dm(self, *args, **kwargs):
        self.mock(*args, **kwargs)
        return

    def get_channel_info(self, *args, **kwargs):
        self.mock(*args, **kwargs)
        return self.channel_info

    def get_user_timezone(self, *args, **kwargs):
        self.mock(*args, **kwargs)
        return self.timezone_info

    def post_ephemeral_message(self, *args, **kwargs):
        self.mock(*args, **kwargs)
        return

    def post_message(self, *args, **kwargs):
        self.mock(*args, **kwargs)
        return

    def display_app_home(self, *args, **kwargs):
        self.mock(*args, **kwargs)
        return

    def __repr__(self):
        return "<FakeSlackClient>"
