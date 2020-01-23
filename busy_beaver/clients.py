from .adapters import MeetupAdapter
from .config import MEETUP_API_KEY

meetup = MeetupAdapter(MEETUP_API_KEY)
